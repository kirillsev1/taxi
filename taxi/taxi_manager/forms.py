"""Forms for views."""
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.forms import CharField, ChoiceField, DateField, DecimalField, EmailField, Form, IntegerField
from django.forms.widgets import RadioSelect, TextInput
from taxi_manager.form_functions import check, find_available_drivers, get_point, get_rates, is_order_active
from taxi_manager.models import Car, CarOrder, Customer, Driver, Order

from taxi.config import MAX_STR_LEN, car_choices


class DriverRegistrationForm(Form):
    """Form for driver registration."""

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
        """
        Save the driver registration form and create a new driver instance.

        Args:
            location_str: The location as a string.

        Returns:
            Driver: The created driver instance.
        """
        error = check(self.cleaned_data, location_str)
        if error:
            return error

        location_lat, location_lon = location_str.split(',')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password1')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        rate = self.cleaned_data.get('rate')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        car_type = next((car[0] for car in car_choices if rate in car), None)
        car = Car.objects.create(
            created=self.cleaned_data.get('created'),
            manufacturer=self.cleaned_data.get('manufacturer'),
            capacity=self.cleaned_data.get('capacity'),
            number=self.cleaned_data.get('number'),
            mark=self.cleaned_data.get('mark'),
            rate=car_type,
        )

        if location_lat and location_lon:
            location = Point(float(location_lon), float(location_lat))
            driver = Driver.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone'),
                location=location,
                car=car,
            )
            driver.save()
            return driver


class CustomerRegistrationForm(Form):
    """Form for customer registration."""

    username = CharField(max_length=100)
    first_name = CharField(max_length=MAX_STR_LEN)
    last_name = CharField(max_length=MAX_STR_LEN)
    email = EmailField()
    phone = CharField(max_length=MAX_STR_LEN // 2)
    password1 = CharField(max_length=100)
    password2 = CharField(max_length=100)

    def save(self):
        """
        Save the customer registration form and create a new customer instance.

        Returns:
            str or None: Error message or None if successful.
        """
        cleaned_data = self.cleaned_data

        username = cleaned_data.get('username')
        password1 = cleaned_data.get('password1')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        error = check(self.cleaned_data)
        if error:
            return error

        user = User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        customer = Customer.objects.create(user=user, phone=phone)
        customer.save()


class LoginForm(Form):
    """Form for user login."""

    username = CharField()
    password = CharField()


class OrderFrom(Form):
    """Form for creating an order."""

    departure = CharField(widget=TextInput(attrs={'id': 'departure-input'}))
    arrival = CharField(widget=TextInput(attrs={'id': 'arrival-input'}))
    rate = ChoiceField(widget=RadioSelect(), choices=car_choices)

    def save(self, request):
        """
        Save the order form and create a new order instance.

        Args:
            request: The HTTP request.

        Returns:
            str or None: Error message or None if successful.
        """
        order = Order.objects.create(
            customer=Customer.objects.get(user=request.user),
            departure=get_point(self.cleaned_data.get('departure')),
            arrival=get_point(self.cleaned_data.get('arrival')),
            rate=self.cleaned_data.get('rate'),
            rating=5,
            status='active',
        )
        order.save()

        higher_rates = get_rates(int(self.cleaned_data.get('rate')) - 1)
        distance = [5000, 12000, 1000]

        drivers = find_available_drivers(order, higher_rates, distance)
        if isinstance(drivers, str):
            return drivers
        if drivers:
            for driver in drivers:
                car = driver.car
                if is_order_active(driver):
                    CarOrder.objects.get_or_create(car=car, order=order)
            return None


class CostForm(Form):
    """Form for entering the order cost."""

    cost = DecimalField()

    def save(self, order_id):
        """
        Update the order cost based on the cost form.

        Args:
            order_id: The ID of the order.
        """
        order_cost = self.cleaned_data.get('cost')
        if order_cost > 0:
            Order.objects.filter(id=order_id).update(cost=order_cost)


class EvaluationForm(Form):
    """Form for evaluating an order."""

    rating = DecimalField()

    def save(self, order_id):
        """
        Update the order rating based on the evaluation form.

        Args:
            order_id: The ID of the order.

        Returns:
            str or None: Error message or None if successful.
        """
        order = Order.objects.filter(id=order_id)
        order_rate = self.cleaned_data.get('rating')
        if 0 <= order_rate <= 5 and order[0].status == 'evaluation':
            order.update(rating=order_rate, status='completed')
        else:
            return 'Please enter a number between 0 and 5 for the rating.'
