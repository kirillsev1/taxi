from django.contrib.auth.models import User
from .models import Driver, Customer, Car, Order, CarOrder
from rest_framework.serializers import HyperlinkedModelSerializer


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        lookup_field = "id"
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')


class CarSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Car
        lookup_field = "id"
        fields = ('id', 'created', 'manufacturer', 'rate', 'capacity', 'number', 'mark')


class DriverSerializer(HyperlinkedModelSerializer):
    user = UserSerializer()
    car = CarSerializer()

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        car = Car.objects.create(**validated_data.pop('car'))
        driver = Driver.objects.create(user=user, car=car, **validated_data)
        return driver

    class Meta:
        model = Driver
        lookup_field = "id"
        fields = ('id', 'user', 'phone', 'car')


class CustomerSerializer(HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        lookup_field = "id"
        fields = ('id', 'user', 'phone')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class OrderSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Order
        lookup_field = "id"
        geo_field = "arrival"
        fields = (
            'id',
            'created',
            'customer',
            'driver',
            'rating',
            'departure',
            'order_date',
            'arrival',
            'cost',
            'rate',
            'status'
        )


class CarOrderSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = CarOrder
        lookup_field = "id"
        fields = ('id', 'car', 'order')
