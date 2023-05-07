from django.contrib.gis.geos import Point, GEOSGeometry
from django.forms import Form, ChoiceField, DecimalField, EmailField, CharField, IntegerField, DateTimeField
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, DateTimeInput, RadioSelect
from taxi_manager.models import Driver, Car, Customer, Order, CarOrder


class DriverRegistrationForm(Form):
    username = CharField(max_length=100)
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    email = EmailField()
    phone = CharField(max_length=15)
    password1 = CharField(max_length=100)
    password2 = CharField(max_length=100)

    created = DateTimeField()
    manufacturer = CharField(max_length=40)
    capacity = IntegerField()
    number = CharField(max_length=10)
    mark = CharField(max_length=40)
    rate = CharField(max_length=8)

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email')
        )
        car = Car.objects.create(
            created=self.cleaned_data.get('created'),
            manufacturer=self.cleaned_data.get('manufacturer'),
            capacity=self.cleaned_data.get('capacity'),
            number=self.cleaned_data.get('number'),
            mark=self.cleaned_data.get('mark'),
            rate=self.cleaned_data.get('rate'),
        )
        driver = Driver.objects.create(user=user, phone=self.cleaned_data.get('phone'), car=car)
        driver.save()
        return driver


class CustomerRegistrationForm(Form):
    username = CharField(max_length=100)
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    email = EmailField()
    phone = CharField(max_length=15)
    password1 = CharField(max_length=100)
    password2 = CharField(max_length=100)

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email')
        )
        customer = Customer.objects.create(user=user, phone=self.cleaned_data.get('phone'))
        print(customer)
        customer.save()


class LoginForm(Form):
    username = CharField()
    password = CharField()


car_choices = (('economy', 'economy'), ('comfort', 'comfort'), ('business', 'business'))


def get_point(points):
    x, y = points.split(',')
    return Point(float(x), float(y), srid=4326)


def get_objects_by_field(model, field_name, field_value):
    queryset = model.objects.filter(**{field_name: field_value})
    return list(queryset)


class OrderFrom(Form):
    departure = CharField(widget=TextInput(attrs={'id': 'departure-input'}))
    arrival = CharField(widget=TextInput(attrs={'id': 'arrival-input'}))
    order_date = DateTimeField(widget=DateTimeInput(attrs={'id': 'order-date-input'}))
    rate = ChoiceField(widget=RadioSelect(), choices=car_choices)

    def save(self, request):
        order = Order.objects.create(
            customer=Customer.objects.get(user=request.user),
            departure=get_point(self.cleaned_data.get('departure')),
            arrival=get_point(self.cleaned_data.get('arrival')),
            order_date=self.cleaned_data.get('order_date'),
            rate=self.cleaned_data.get('rate'),
            rating=5,
            status='active'
        )
        print(order)
        order.save()
        drivers = Driver.objects.filter(location__dwithin=(GEOSGeometry(order.departure), D(m=5000), 90))
        for driver in drivers:
            car = driver.car
            if not Order.objects.filter(driver=driver, status='active').exists():
                CarOrder.objects.get_or_create(car=car, order=order)


class CostForm(Form):
    cost = DecimalField()

    def save(self, order_id):
        order_cost = self.cleaned_data.get('cost')
        if order_cost > 0:
            Order.objects.filter(id=order_id).update(cost=order_cost)
