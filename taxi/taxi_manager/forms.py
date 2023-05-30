import datetime
from time import monotonic, sleep
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db import transaction
from django.forms import Form, ChoiceField, DecimalField, EmailField, CharField, IntegerField, DateField
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, RadioSelect
from taxi_manager.models import Driver, Car, Customer, Order, CarOrder

car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)
NUMBER_LEN = 11
MAX_STR_LEN = 30
SRID = 4326
CARS_CREATION_YEAR = (1885, 1, 29)


class DriverRegistrationForm(Form):
    username = CharField(max_length=100)
    first_name = CharField(max_length=MAX_STR_LEN)
    last_name = CharField(max_length=MAX_STR_LEN)
    email = EmailField()
    phone = CharField(max_length=MAX_STR_LEN // 2)
    password1 = CharField(max_length=100)
    password2 = CharField(max_length=100)

    created = DateField()
    manufacturer = CharField(max_length=MAX_STR_LEN)
    capacity = IntegerField()
    number = CharField(max_length=10)
    mark = CharField(max_length=MAX_STR_LEN)
    rate = ChoiceField(choices=car_choices, widget=RadioSelect(attrs={'class': 'rate-input'}))

    def save(self, location_str):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            return 'passwords are different'
        try:
            location_lat, location_lon = location_str.split(',')
        except Exception:
            return 'Access your geolocation'
        if not self.cleaned_data.get('phone').startswith('+7') or len(self.cleaned_data.get('phone')) != NUMBER_LEN:
            return 'wrong phone'
        if self.cleaned_data.get('created') < datetime.date(*CARS_CREATION_YEAR):
            return 'cars were not created yet'
        if datetime.date.today() < self.cleaned_data.get('created'):
            return f'Sorry we can`t travel in time it is {datetime.date.today().year} year'
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
        )
        rate = self.cleaned_data.get('rate')
        for car_type in car_choices:
            if rate in car_type:
                rate = car_type[0]
        car = Car.objects.create(
            created=self.cleaned_data.get('created'),
            manufacturer=self.cleaned_data.get('manufacturer'),
            capacity=self.cleaned_data.get('capacity'),
            number=self.cleaned_data.get('number'),
            mark=self.cleaned_data.get('mark'),
            rate=rate,
        )

        if location_lat and location_lon:
            location = Point(float(location_lon), float(location_lat))
            driver = Driver.objects.create(user=user, phone=self.cleaned_data.get('phone'), location=location, car=car)
            driver.save()
            return driver


class CustomerRegistrationForm(Form):
    username = CharField(max_length=100)
    first_name = CharField(max_length=MAX_STR_LEN)
    last_name = CharField(max_length=MAX_STR_LEN)
    email = EmailField()
    phone = CharField(max_length=MAX_STR_LEN // 2)
    password1 = CharField(max_length=100)
    password2 = CharField(max_length=100)

    def save(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            return 'passwords are different'
        if not self.cleaned_data.get('phone').startswith('+7') or len(self.cleaned_data.get('phone')) != NUMBER_LEN:
            return 'wrong phone'
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
        )
        customer = Customer.objects.create(user=user, phone=self.cleaned_data.get('phone'))
        customer.save()


class LoginForm(Form):
    username = CharField()
    password = CharField()


def get_point(points):
    x_pos, y_pos = points.split(',')
    return Point(float(x_pos), float(y_pos), srid=SRID)


def get_objects_by_field(model, field_name, field_value):
    queryset = model.objects.filter(**{field_name: field_value})
    return list(queryset)


class OrderFrom(Form):
    departure = CharField(widget=TextInput(attrs={'id': 'departure-input'}))
    arrival = CharField(widget=TextInput(attrs={'id': 'arrival-input'}))
    rate = ChoiceField(widget=RadioSelect(), choices=car_choices)

    def save(self, request):
        order = Order.objects.create(
            customer=Customer.objects.get(user=request.user),
            departure=get_point(self.cleaned_data.get('departure')),
            arrival=get_point(self.cleaned_data.get('arrival')),
            rate=self.cleaned_data.get('rate'),
            rating=5,
            status='active',
        )
        order.save()
        current_rate_index = int(self.cleaned_data.get('rate')) - 1

        higher_rates = [car_choices[ind][0] for ind in range(current_rate_index, len(car_choices))]
        start = monotonic()
        distance = [5000, 12000, 1000]
        while True:
            for radius in range(*distance):
                if monotonic() - start >= 10:
                    order.delete()
                    return 'No free drivers behind you'
                for rate in higher_rates:
                    drivers = Driver.objects.filter(
                        location__dwithin=(GEOSGeometry(order.departure), D(m=radius), 90),
                        car__rate=rate,
                    )
                    if drivers:
                        for driver in drivers:
                            car = driver.car
                            if not Order.objects.filter(driver=driver, status='active').exists():
                                CarOrder.objects.get_or_create(car=car, order=order)
                        return None
                    else:
                        sleep(1)


class CostForm(Form):
    cost = DecimalField()

    @transaction.atomic
    def save(self, order_id):
        order_cost = self.cleaned_data.get('cost')
        if order_cost > 0:
            Order.objects.filter(id=order_id).update(cost=order_cost)


class EvaluationForm(Form):
    rating = DecimalField()

    @transaction.atomic
    def save(self, order_id):
        order = Order.objects.filter(id=order_id)
        order_rate = self.cleaned_data.get('rating')
        if order_rate > 0 and order[0].status == 'evaluation':
            order.update(rating=order_rate, status='completed')
