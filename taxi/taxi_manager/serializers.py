"""Serializers for REST."""
from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer

from taxi_manager.models import Car, CarOrder, Customer, Driver, Order
from taxi.config import ID_STR, USER_STR


class UserSerializer(HyperlinkedModelSerializer):
    """Serializer for the User model."""

    class Meta:
        """Class Meta for UserSerializer."""

        model = User
        lookup_field = ID_STR
        fields = (ID_STR, 'username', 'password', 'first_name', 'last_name', 'email')


class CarSerializer(HyperlinkedModelSerializer):
    """Serializer for the Car model."""

    class Meta:
        """Class Meta for CarSerializer."""

        model = Car
        lookup_field = ID_STR
        fields = (ID_STR, 'created', 'manufacturer', 'rate', 'capacity', 'number', 'mark')


class DriverSerializer(HyperlinkedModelSerializer):
    """Serializer for the Driver model."""

    user = UserSerializer()
    car = CarSerializer()

    class Meta:
        """Class Meta for DriverSerializer."""

        model = Driver
        lookup_field = ID_STR
        fields = (ID_STR, USER_STR, 'phone', 'car')

    def create(self, validated_data):
        """
        Create a Driver instance with user and car credentials.

        Args:
            validated_data: Validated data for creating the Driver.

        Returns:
            Customer: Created Driver instance.
        """
        user_data = validated_data.pop(USER_STR)
        user = User.objects.create_user(**user_data)
        car = Car.objects.create(**validated_data.pop('car'))
        return Driver.objects.create(user=user, car=car, **validated_data)


class CustomerSerializer(HyperlinkedModelSerializer):
    """Serializer for the Customer model."""

    user = UserSerializer()

    class Meta:
        """Class Meta for CustomerSerializer."""

        model = Customer
        lookup_field = ID_STR
        fields = (ID_STR, USER_STR, 'phone')

    def create(self, validated_data):
        """
        Create a Customer instance with user credentials.

        Args:
            validated_data: Validated data for creating the Customer.

        Returns:
            Customer: Created Customer instance.
        """
        user_data = validated_data.pop(USER_STR)
        user = User.objects.create_user(**user_data)
        return Customer.objects.create(user=user, **validated_data)


class OrderSerializer(HyperlinkedModelSerializer):
    """Serializer for the Order model."""

    class Meta:
        """Class Meta for OrderSerializer."""

        model = Order
        lookup_field = ID_STR
        geo_field = 'arrival'
        fields = (
            ID_STR,
            'created',
            'customer',
            'driver',
            'rating',
            'departure',
            'order_date',
            'arrival',
            'cost',
            'rate',
            'status',
        )


class CarOrderSerializer(HyperlinkedModelSerializer):
    """Serializer for the CarOrder model."""

    class Meta:
        """Class Meta for CarOrderSerializer."""

        model = CarOrder
        lookup_field = ID_STR
        fields = (ID_STR, 'car', 'order')
