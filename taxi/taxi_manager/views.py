from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.db.utils import IntegrityError
from django.contrib.auth import decorators as auth_decorators, mixins as auth_mixins, login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from rest_framework import decorators, viewsets, parsers, status as status_codes, permissions, status, generics
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import models, transaction

from taxi_manager.forms import DriverRegistrationForm, CustomerRegistrationForm, LoginForm, OrderFrom, CostForm
from taxi_manager.models import Car, Driver, Customer, Order, CarOrder
from taxi_manager.serializers import CarSerializer, DriverSerializer, CustomerSerializer, OrderSerializer, \
    CarOrderSerializer, UserSerializer


# Create your views here.
@auth_decorators.login_required
def profile_page(request):
    user = request.user
    try:
        driver = Driver.objects.get(user=user)
    except Exception:
        driver = False
    try:
        customer = Customer.objects.get(user=user)
    except Exception:
        customer = False
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            try:
                form.save(request.POST.get('order_id'))
            except IntegrityError:
                return redirect('/profile/')
            return redirect('/profile/')

    query_user = User.objects.get_by_natural_key(username=user)
    data = {
        'user': {i: j for i, j in query_user.__dict__.items() if
                 i in ['id', 'username', 'first_name', 'last_name', 'email']},
    }

    if driver:
        car = Car.objects.get(id=driver.__dict__['car_id'])
        data['car'] = {i: j for i, j in car.__dict__.items() if i not in ['id', '_state']}
        data['driver_phone'] = driver.__dict__['phone']
    if customer:
        data['orders'] = get_objects_by_field(Order, 'customer', Customer.objects.get(user=user))
        data['customer_phone'] = customer.__dict__['phone']
        data['form'] = CostForm()
    return render(request, 'taxi/profile.html', {'data': data})


def index(request):
    return render(request, 'taxi/index.html')


def get_objects_by_field(model, field_name, field_value):
    queryset = model.objects.filter(**{field_name: field_value}).order_by('order_date')
    return list(queryset)


@auth_decorators.login_required
def drivers_orders_page(request):
    if request.method == 'POST':
        order_id = request.POST.get('order')
        if order_id:
            order = Order.objects.get(id=order_id)
            car_order_qs = CarOrder.objects.filter(Q(order=order))
            car_order_qs.delete()
            order.driver = Driver.objects.get(user=request.user)
            order.status = 'executed'
            order.save()
            return redirect('/profile/')
        order_end_id = request.POST.get('order_end')
        if order_end_id:
            order = Order.objects.get(id=order_end_id)
            car_order_qs = CarOrder.objects.filter(Q(order=order))
            car_order_qs.delete()
            order.status = 'completed'
            order.save()

            driver = order.driver
            driver.location = order.arrival
            driver.save()
            return redirect('/profile/')
    try:
        car_id = Driver.objects.get(user=request.user).__dict__.get('car_id')
        car = Car.objects.get(id=car_id)
        order = CarOrder.objects.get(car=car)
    except Exception:
        order = 'No ordders'

    try:
        order = Order.objects.get(driver__user__username=request.user, status='executed')
        print(order)
    except Exception as ex:
        print(ex)
    return render(request, 'taxi/driver_orders.html', {'order': order})


@auth_decorators.login_required
def order_page(request):
    try:
        Customer.objects.get(user=request.user)
    except Exception:
        return redirect('/driver_orders/')
    if request.method == 'POST':
        form = OrderFrom(request.POST)
        if form.is_valid():
            try:
                form.save(request)
            except IntegrityError:
                return render(request, 'taxi/order_page.html', {'form': form, 'error': 'Something gone wrong'})
            return redirect('/profile/')
    else:
        form = OrderFrom()
    return render(request, "taxi/order_page.html", {'form': form})


class Permission(permissions.BasePermission):
    def has_permission(self, request, _):
        if request.method in ['GET', 'HEAD', 'PATCH']:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in ['POST', 'PUT', 'DELETE']:
            return bool(request.user and request.user.is_superuser)
        return False


def query_from_request(request, cls_serializer=None) -> dict:
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET


def create_viewset(cls_model: models.Model, serializer):
    class CustomViewSet(viewsets.ModelViewSet):
        serializer_class = serializer
        queryset = cls_model.objects.all()
        permission_classes = [Permission]

        # def get_object(self):
        #     queryset = self.filter_queryset(self.get_queryset())
        #     try:
        #         obj = queryset.get(pk=self.request.GET.get('id'))
        #     except:
        #         obj = None
        #     self.check_object_permissions(self.request, obj)
        #     return obj

        def get_queryset(self):
            instances = cls_model.objects.all()
            query = query_from_request(self.request, serializer)
            if query:
                instances = instances.filter(**query)
            return instances

        def delete(self, request):
            query = query_from_request(request, serializer)
            if query:
                instances = cls_model.objects.filter(**query)
                objects_num = len(instances)
                if not objects_num:
                    msg = f'DELETE query {query} did not match any instances of {cls_model.__name__}'
                    return Response(msg, status=status_codes.HTTP_404_NOT_FOUND)
                try:
                    instances.delete()
                except Exception as error:
                    return Response(error, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
                msg = f'DELETED {objects_num} instances of {cls_model.__name__}'
                status = status_codes.HTTP_204_NO_CONTENT if objects_num == 1 else status_codes.HTTP_200_OK
                return Response(msg, status=status)
            return Response('DELETE has got no query', status=status_codes.HTTP_400_BAD_REQUEST)

        def put(self, request):
            def serialize(target):
                payload = parsers.JSONParser().parse(request)
                if target:
                    serialized = serializer(target, data=payload, partial=True)
                    status = status_codes.HTTP_200_OK
                    body = f'PUT has updated instance of {cls_model.__name__} id={target.id}'
                else:
                    serialized = serializer(data=payload, partial=True)
                    status = status_codes.HTTP_201_CREATED
                    body = f'PUT has created a new instance of {cls_model.__name__}'

                if not serialized.is_valid():
                    return status_codes.HTTP_400_BAD_REQUEST, f'PUT could not process content: {payload}'

                try:
                    serialized.save()
                except Exception as error:
                    return status_codes.HTTP_500_INTERNAL_SERVER_ERROR, error
                return status, body

            query = query_from_request(request, serializer)
            target_id = query.get('id', '')
            if target_id:
                target_object = cls_model.objects.get(id=target_id)
                status, body = serialize(target_object)
                return Response(body, status=status)
            return Response('PUT has got no id primary key', status=status_codes.HTTP_400_BAD_REQUEST)

    return CustomViewSet


def driver_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            try:
                driver = form.save()
                location_lat = request.POST.get('location').split(',')[0]
                location_lon = request.POST.get('location').split(',')[1]
                if location_lat and location_lon:
                    driver.location = Point(float(location_lon), float(location_lat))
                    driver.save()
            except IntegrityError:
                return render(request, 'registration/register.html', {'form': form, 'error': 'User with such username already exists'})
            return redirect('/login/')
    else:
        form = DriverRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def customer_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                return render(request, 'registration/register.html', {'form': form, 'error': 'User with such username already exists'})
            return redirect('/login/')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


UserViewSet = create_viewset(User, UserSerializer)
CarViewSet = create_viewset(Car, CarSerializer)
DriverViewSet = create_viewset(Driver, DriverSerializer)
PassengerViewSet = create_viewset(Customer, CustomerSerializer)
OrderViewSet = create_viewset(Order, OrderSerializer)
CarOrderViewSet = create_viewset(CarOrder, CarOrderSerializer)
