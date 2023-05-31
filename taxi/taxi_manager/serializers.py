from django.contrib.auth.models import User
from taxi_manager.models import Driver, Customer, Car, Order, CarOrder
from rest_framework.serializers import HyperlinkedModelSerializer

ID_STR = 'id'
USER_STR = 'user'


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        lookup_field = ID_STR
        fields = (ID_STR, 'username', 'password', 'first_name', 'last_name', 'email')


class CarSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Car
        lookup_field = ID_STR
        fields = (ID_STR, 'created', 'manufacturer', 'rate', 'capacity', 'number', 'mark')


class DriverSerializer(HyperlinkedModelSerializer):
    user = UserSerializer()
    car = CarSerializer()

    def create(self, validated_data):
        user_data = validated_data.pop(USER_STR)
        user = User.objects.create_user(**user_data)
        car = Car.objects.create(**validated_data.pop('car'))
        return Driver.objects.create(user=user, car=car, **validated_data)

    class Meta:
        model = Driver
        lookup_field = ID_STR
        fields = (ID_STR, USER_STR, 'phone', 'car')


class CustomerSerializer(HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        lookup_field = ID_STR
        fields = (ID_STR, USER_STR, 'phone')

    def create(self, validated_data):
        user_data = validated_data.pop(USER_STR)
        user = User.objects.create_user(**user_data)
        return Customer.objects.create(user=user, **validated_data)


class OrderSerializer(HyperlinkedModelSerializer):
    class Meta:
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
    class Meta:
        model = CarOrder
        lookup_field = ID_STR
        fields = (ID_STR, 'car', 'order')
