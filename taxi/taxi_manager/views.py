from django.contrib.auth import decorators as auth_decorators
from django.contrib.auth import models
from django.core.exceptions import ObjectDoesNotExist
from django.db import utils
from django.shortcuts import redirect, render
from rest_framework import permissions

from taxi_manager.forms import CustomerRegistrationForm, DriverRegistrationForm, OrderFrom
from taxi_manager.models import Car, CarOrder, Customer, Driver, Order
from taxi_manager.serializers import CarOrderSerializer, CarSerializer, CustomerSerializer, DriverSerializer, \
    OrderSerializer, UserSerializer
from taxi_manager.view_functions import create_viewset, get_order, handle_customer_response
from taxi_manager.view_handlers import handle_customer_data, handle_driver_data, handle_driver_resp, handle_eval_form

car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)

REG_TEMPLATE = 'registration/register.html'
ERROR = 'error'
FORM = 'form'
POST = 'POST'
PROFILE_URL = '/profile/'
LOGIN_URL = '/login/'
ORDER_PAGE_TEMPLATE = 'taxi/order_page.html'
DRIVER_ORDER_URL = '/driver_order/'
DRIVER_ORDER_TEMPLATE = 'taxi/driver_order.html'
CUSTOMER_ORDER_URL = '/customer_order/'
INDEX_TEMPLATE = 'taxi/index.html'


class Permission(permissions.BasePermission):
    def has_permission(self, request, _):
        if request.method in {'GET', 'HEAD', 'OPTIONS', 'PATCH'}:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in {'POST', 'PUT', 'DELETE'}:
            return bool(request.user and request.user.is_superuser)
        return False


@auth_decorators.login_required
def profile_page(request):
    user = request.user
    driver = Driver.objects.filter(user=user)
    customer = Customer.objects.filter(user=user)

    if request.method == POST:
        handle_customer_response(request)
        handle_eval_form(request)

    query_user = models.User.objects.get_by_natural_key(username=user)
    user_data = {'user': query_user}

    if driver:
        handle_driver_data(driver, user_data)
    if customer:
        handle_customer_data(customer, user_data)

    return render(request, 'taxi/profile.html', {'data': user_data})


def index(request):
    return render(request, INDEX_TEMPLATE)


@auth_decorators.login_required
def driver_order_page(request):
    try:
        Driver.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect(CUSTOMER_ORDER_URL)

    if request.method == POST:
        order_id = request.GET.get('order_id')
        driver_response = request.POST.get('answer')
        handle_driver_resp(request, order_id, driver_response)

    return render(request, DRIVER_ORDER_TEMPLATE, {'order': get_order(request)})


@auth_decorators.login_required
def order_page(request):
    try:
        Customer.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect(DRIVER_ORDER_URL)
    if request.method == POST:
        form = OrderFrom(request.POST)
        if form.is_valid():
            try:
                order = form.save(request)
            except utils.IntegrityError:
                return render(request, ORDER_PAGE_TEMPLATE, {FORM: form, ERROR: 'Something gone wrong'})
            if isinstance(order, str):
                return render(request, ORDER_PAGE_TEMPLATE, {FORM: form, ERROR: order})
            return redirect(PROFILE_URL)
    else:
        form = OrderFrom()
    return render(request, ORDER_PAGE_TEMPLATE, {FORM: form})


def driver_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == POST:
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            try:
                driver = form.save(request.POST.get('location'))
            except utils.IntegrityError:
                return render(
                    request,
                    REG_TEMPLATE,
                    {FORM: form, ERROR: 'User with such username already exists'},
                )
            if isinstance(driver, str):
                return render(
                    request,
                    REG_TEMPLATE,
                    {FORM: form, ERROR: driver},
                )
            driver.save()
            return redirect(LOGIN_URL)
    else:
        form = DriverRegistrationForm()

    return render(request, REG_TEMPLATE, {FORM: form})


def customer_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == POST:
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                customer = form.save()
            except utils.IntegrityError:
                return render(
                    request,
                    REG_TEMPLATE,
                    {FORM: form, ERROR: 'User with such username already exists'},
                )
            if isinstance(customer, str):
                return render(request, REG_TEMPLATE, {FORM: form, ERROR: customer})
            return redirect(LOGIN_URL)
    else:
        form = CustomerRegistrationForm()

    return render(request, REG_TEMPLATE, {FORM: form})


UserViewSet = create_viewset(models.User, UserSerializer, Permission)
CarViewSet = create_viewset(Car, CarSerializer, Permission)
DriverViewSet = create_viewset(Driver, DriverSerializer, Permission)
PassengerViewSet = create_viewset(Customer, CustomerSerializer, Permission)
OrderViewSet = create_viewset(Order, OrderSerializer, Permission)
CarOrderViewSet = create_viewset(CarOrder, CarOrderSerializer, Permission)
