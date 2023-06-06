"""Models for DB."""
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.db import models

from taxi.config import car_choices, order_statuses, NUMBER_LEN, MAX_STR_LEN, SRID, RUBLE, STARTING_COST


class UUIDMixin(models.Model):
    """Mixin class for adding UUID field to models."""

    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)

    class Meta:
        """Class Meta for UUIDMixin."""

        abstract = True


class Car(UUIDMixin):
    """Model representing a car."""

    created = models.DateTimeField(auto_now=True)
    manufacturer = models.CharField(max_length=MAX_STR_LEN)
    capacity = models.IntegerField()
    number = models.CharField(max_length=10)
    mark = models.CharField(max_length=MAX_STR_LEN)
    rate = models.CharField(max_length=8, choices=car_choices)

    class Meta:
        """Class Meta for Car."""

        db_table = 'car'

    def __str__(self):
        """
        Return a string representation of the Car.

        Returns:
            str: The string representation of the Car.
        """
        return 'Manufacture: {0} - Number: {1}'.format(self.manufacturer, self.number)


class Driver(UUIDMixin):
    """Model representing a driver."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    phone = models.CharField(max_length=MAX_STR_LEN, null=False, blank=False, default='+0000000000000')
    location = PointField(srid=SRID, blank=True, null=True)

    class Meta:
        """Class Meta for Driver."""

        db_table = 'driver'

    def delete(self, *args, **kwargs):
        """
        Delete the Driver instance along with its associated User instance.

        Args:
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.
        """
        self.user.delete()
        super().delete(*args, **kwargs)

    def clean(self):
        """
        Validate the phone number of the Driver instance.

        Raises:
            ValidationError: If the phone number is not in the correct format.
        """
        if not self.phone.startswith('+') or len(self.phone) != NUMBER_LEN:
            raise ValidationError('phone must start with + and number of digits nust be 10')

    def __str__(self):
        """
        Return a string representation of the Driver.

        Returns:
            str: The string representation of the Driver.
        """
        user = self.user
        return 'First name: {0} - Last name: {1}'.format(user.first_name, user.last_name)


class Customer(UUIDMixin):
    """Model representing a customer."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=MAX_STR_LEN, null=False, blank=False, default='+0000000000000')

    class Meta:
        """Class Meta for Customer."""

        db_table = 'customer'

    def delete(self, *args, **kwargs):
        """
        Delete the Customer instance along with its associated User instance.

        Args:
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.
        """
        self.user.delete()
        super().delete(*args, **kwargs)

    def clean(self):
        """
        Validate the phone number of the Driver instance.

        Raises:
            ValidationError: If the phone number is not in the correct format.
        """
        if not self.phone.startswith('+') or len(self.phone) != NUMBER_LEN:
            raise ValidationError('Phone must start with "+" and have a length of 10 digits.')

    def __str__(self):
        """
        Return a string representation of the Customer.

        Returns:
            str: The string representation of the Customer.
        """
        user = self.user
        return '{0} {1}'.format(user.first_name, user.last_name)


class Order(UUIDMixin):
    """Model representing an order."""

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

    class Meta:
        """Class Meta for Order."""

        db_table = 'order'

    def save(self, *args, **kwargs):
        """
        Calculate and set the cost based on the departure and arrival points before saving the Order instance.

        Args:
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.
        """
        if self.departure and self.arrival:
            distance = self.departure.distance(self.arrival)
            self.cost = distance * STARTING_COST * RUBLE
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a string representation of the Order.

        Returns:
            str: The string representation of the Order.
        """
        return 'Driver: {0} = Customer: {1}'.format(self.driver, self.customer)


class CarOrder(UUIDMixin):
    """Model representing a car order."""

    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        """Class Meta for CarOrder."""

        db_table = 'car_order'

    def __str__(self):
        """
        Return a string representation of the CarOrder.

        Returns:
            str: The string representation of the CarOrder.
        """
        return 'Car: {0} | Order: {1}'.format(self.car, self.order)
