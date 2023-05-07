from django.contrib.gis.db.models import PointField
from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User
from django.utils import timezone

car_choices = (('economy', 'economy'), ('comfort', 'comfort'), ('business', 'business'))


# Create your models here.
class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)

    class Meta:
        abstract = True


class Car(UUIDMixin):
    created = models.DateTimeField(auto_now=True)
    manufacturer = models.CharField(max_length=40)
    capacity = models.IntegerField()
    number = models.CharField(max_length=10)
    mark = models.CharField(max_length=40)
    rate = models.CharField(max_length=8, choices=car_choices)

    def __str__(self):
        return f'Manufacture: {self.manufacturer} Number: {self.number}'

    class Meta:
        db_table = 'car'


class Driver(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="00000000000000")

    def __str__(self):
        return f'{self.user}'

    class Meta:
        db_table = 'driver'


class Customer(UUIDMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="00000000000000")

    def __str__(self):
        return f'{self.user}'

    class Meta:
        db_table = 'customer'


class Order(UUIDMixin):
    created = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    departure = models.CharField(srid=4326, blank=True, null=True, )
    order_date = models.DateTimeField(auto_now=True)
    arrival = models.CharField(srid=4326, blank=True, null=True,)
    cost = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    rate = models.CharField(max_length=8, choices=car_choices)

    class Meta:
        db_table = 'order'


class CarOrder(UUIDMixin):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'car_order'
