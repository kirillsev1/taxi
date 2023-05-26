from django.contrib.auth.models import User
from django.db.models import Q
from django.db.utils import IntegrityError
from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from taxi_manager.forms import DriverRegistrationForm, CustomerRegistrationForm, OrderFrom, EvaluationForm
from taxi_manager.models import Car, Driver, Customer, Order, CarOrder
from taxi_manager.serializers import CarSerializer, DriverSerializer, CustomerSerializer, OrderSerializer, \
    CarOrderSerializer, UserSerializer

car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)


@auth_decorators.login_required
def profile_page(request):
    user = request.user
    driver = Driver.objects.filter(user=user)
    customer = Customer.objects.filter(user=user)
    if request.method == 'POST':
        customer_response = request.POST.get('answer')
        if customer_response == 'Отозвать заказ':
            Order.objects.filter(customer__user=request.user, id=request.POST.get('order_id')).delete()
            return redirect('/profile/')
        evaluation_form = EvaluationForm(request.POST)
        if evaluation_form.is_valid():
            try:
                evaluation_form.save(request.POST.get('order_id'))
            except IntegrityError:
                return redirect('/profile/')
            return redirect('/profile/')

    query_user = User.objects.get_by_natural_key(username=user)
    data = {
        'user': query_user,
    }

    if driver:
        car = driver[0].car
        data['car'] = car
        data['driver_phone'] = driver[0].phone
        data['orders'] = list(get_objects(Order, 'driver', driver[0]).order_by('order_date'))
    if customer:
        data['orders'] = list(get_objects(Order, 'customer', customer[0]).order_by('order_date'))
        data['customer_phone'] = customer[0].phone
        data['rate_form'] = EvaluationForm()
        data['car_choices'] = car_choices
    return render(request, 'taxi/profile.html', {'data': data})


def index(request):
    return render(request, 'taxi/index.html')


def get_objects(model, field_name, field_value):
    queryset = model.objects.filter(**{field_name: field_value})
    return queryset


def save_order(request, order_id):
    order = Order.objects.get(id=order_id)
    car_order_qs = CarOrder.objects.filter(Q(order=order))
    car_order_qs.delete()
    order.driver = Driver.objects.get(user=request.user)
    order.status = 'executed'
    order.save()


def save_ended_order(order_end_id):
    order = Order.objects.get(id=order_end_id)
    car_order_qs = CarOrder.objects.filter(Q(order=order))
    car_order_qs.delete()
    order.status = 'evaluation'
    order.save()
    driver = order.driver
    driver.location = order.arrival
    driver.save()


def get_order(request):
    car_id = Driver.objects.get(user=request.user).__dict__.get('car_id')
    car = Car.objects.get(id=car_id)
    order = CarOrder.objects.filter(car=car)
    driver_order = Order.objects.filter(driver__user=request.user, status='executed')
    if driver_order:
        order = {'order': driver_order}
    return order


@auth_decorators.login_required
def driver_order_page(request):
    try:
        Driver.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect('/customer_order/')
    if request.method == 'POST':
        order_id = request.GET.get('order_id')
        order_end_id = request.GET.get('order_end')
        driver_response = request.POST.get('answer')
        if order_id and driver_response == 'Accept order':
            save_order(request, order_id)
            return redirect('/driver_order/')
        if order_id and driver_response == 'Cancel':
            current_order = CarOrder.objects.filter(car__driver__user=request.user, order_id=order_id)
            current_order.delete()
        if order_end_id:
            save_ended_order(order_end_id)
            return redirect('/profile/')
    return render(request, 'taxi/driver_order.html', {'order': get_order(request)})


@auth_decorators.login_required
def order_page(request):
    try:
        Customer.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect('/driver_order/')
    if request.method == 'POST':
        form = OrderFrom(request.POST)
        if form.is_valid():
            try:
                order = form.save(request)
            except IntegrityError:
                return render(request, 'taxi/order_page.html', {'form': form, 'error': 'Something gone wrong'})
            if isinstance(order, str):
                return render(request, 'taxi/order_page.html', {'form': form, 'error': order})
            return redirect('/profile/')
    else:
        form = OrderFrom()
    return render(request, "taxi/order_page.html", {'form': form})


class Permission(permissions.BasePermission):
    def has_permission(self, request, _):
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'PATCH']:
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


def create_viewset(cls_model: models.Model, serializer, permission, order_field):
    class_name = f"{cls_model.__name__}ViewSet"
    doc = f"API endpoint that allows users to be viewed or edited for {cls_model.__name__}"
    CustomViewSet = type(class_name, (viewsets.ModelViewSet,), {
        "__doc__": doc,
        "serializer_class": serializer,
        "queryset": cls_model.objects.all().order_by(order_field),
        "permission classes": [permission],
        "get_queryset": lambda self, *args, **kwargs: cls_model.objects.filter(**
            query_from_request(self.request, serializer)).order_by(order_field)})

    return CustomViewSet


def driver_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            try:
                driver = form.save(request.POST.get('location'))
            except IntegrityError:
                return render(request, 'registration/register.html',
                              {'form': form, 'error': 'User with such username already exists'})
            if isinstance(driver, str):
                return render(request, 'registration/register.html',
                              {'form': form, 'error': driver})
            driver.save()
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
                customer = form.save()
            except IntegrityError:
                return render(request, 'registration/register.html',
                              {'form': form, 'error': 'User with such username already exists'})
            if isinstance(customer, str):
                return render(request, 'registration/register.html', {'form': form, 'error': customer})
            return redirect('/login/')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


UserViewSet = create_viewset(User, UserSerializer, Permission, 'id')
CarViewSet = create_viewset(Car, CarSerializer, Permission, 'id')
DriverViewSet = create_viewset(Driver, DriverSerializer, Permission, 'id')
PassengerViewSet = create_viewset(Customer, CustomerSerializer, Permission, 'id')
OrderViewSet = create_viewset(Order, OrderSerializer, Permission, 'id')
CarOrderViewSet = create_viewset(CarOrder, CarOrderSerializer, Permission, 'id')
