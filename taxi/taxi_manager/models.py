from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.db import models

from taxi.config import car_choices, order_statuses, NUMBER_LEN, MAX_STR_LEN, SRID, RUBLE, STARTING_COST


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)

    class Meta:
        abstract = True


class Car(UUIDMixin):
    created = models.DateTimeField(auto_now=True)
    manufacturer = models.CharField(max_length=MAX_STR_LEN)
    capacity = models.IntegerField()
    number = models.CharField(max_length=10)
    mark = models.CharField(max_length=MAX_STR_LEN)
    rate = models.CharField(max_length=8, choices=car_choices)

    def __str__(self):
        return 'Manufacture: {0} - Number: {1}'.format(self.manufacturer, self.number)

    class Meta:
        db_table = 'car'
statuses = (
    ('Cancelled', 'Cancelled'),
    ('Confirmed', 'Confirmed'),
    ('Waiting', 'Waiting')
)
class UserAccount(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.UUIDField(blank=True, null=False)
    status = models.CharField(choices=statuses, default='Waiting', null=False, max_length=16)

    class Meta:
        db_table = 'user_account'

class Driver(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    phone = models.CharField(max_length=MAX_STR_LEN, null=False, blank=False, default='+0000000000000')
    location = PointField(srid=SRID, blank=True, null=True)

    def clean(self):
        if not self.phone.startswith('+') or len(self.phone) != NUMBER_LEN:
            raise ValidationError('phone must start with + and number of digits nust be 10')

    def __str__(self):
        user = self.user
        return 'First name: {0} - Last name: {1}'.format(user.first_name, user.last_name)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'driver'


class Customer(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=MAX_STR_LEN, null=False, blank=False, default='+0000000000000')

    def clean(self):
        if not self.phone.startswith('+') or len(self.phone) != NUMBER_LEN:
            raise ValidationError('phone must start with + and number of digits nust be 10')

    def __str__(self):
        user = self.user
        return '{0} {1}'.format(user.first_name, user.last_name)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'customer'


class Order(UUIDMixin):
    created = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    departure = PointField(srid=SRID, blank=True, null=True)
    order_date = models.DateTimeField(auto_now=True)
    arrival = PointField(srid=SRID, blank=True, null=True)
    cost = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    rate = models.CharField(max_length=9, choices=car_choices)
    status = models.CharField(max_length=10, choices=order_statuses)

    def save(self, *args, **kwargs):
        if self.departure and self.arrival:
            distance = self.departure.distance(self.arrival)
            self.cost = distance * STARTING_COST * RUBLE
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Driver: {0} = Customer: {1}'.format(self.driver, self.customer)

    class Meta:
        db_table = 'order'


class CarOrder(UUIDMixin):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Car: {0} | Order: {1}'.format(self.car, self.order)

    class Meta:
        db_table = 'car_order'
