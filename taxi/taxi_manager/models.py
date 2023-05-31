from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models
from uuid import uuid4
from django.core.exceptions import ValidationError

car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)
order_statuses = (
    ('completed', 'completed'),
    ('active', 'active'),
    ('canceled', 'canceled'),
    ('executed', 'executed'),
    ('evaluation', 'evaluation'),
)
NUMBER_LEN = 11
MAX_STR_LEN = 30
SRID = 4326
RUBLE = 84
STARTING_COST = 75


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
        return f'Manufacture: {self.manufacturer} - Number: {self.number}'

    class Meta:
        db_table = 'car'


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
        return f'First name: {user.first_name} - Last name: {user.last_name}'

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
        return f'First name: {user.first_name} - Last name: {user.last_name}'

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
        return f'Driver: {self.driver} = Customer: {self.customer}'

    class Meta:
        db_table = 'order'


class CarOrder(UUIDMixin):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'Car: {self.car} | Order: {self.order}'

    class Meta:
        db_table = 'car_order'
