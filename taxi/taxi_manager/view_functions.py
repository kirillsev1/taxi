"""Functions for views."""
from django.db import models
from django.shortcuts import redirect
from rest_framework import viewsets

from taxi_manager.models import Car, CarOrder, Driver, Order
from taxi.config import PROFILE_URL


def create_viewset(cls_model: models.Model, serializer, permission, order_field='id'):
    """
    Dynamically creates a viewset class for the specified model.

    Args:
        cls_model (models.Model): The model class.
        serializer: The serializer class for the model.
        permission: The permission class for the viewset.
        order_field (str): The field to use for ordering the queryset.

    Returns:
        type: The created viewset class.
    """
    class_name = '{0}ViewSet'.format(cls_model.__name__)
    doc = 'API endpoint that allows users to be viewed or edited for {0}'.format(cls_model.__name__)
    return type(
        class_name,
        (viewsets.ModelViewSet,),
        {
            '__doc__': doc,
            'serializer_class': serializer,
            'queryset': cls_model.objects.all().order_by(order_field),
            'permission_classes': [permission],
            'get_queryset': lambda queryset_self, *args, **kwargs: cls_model.objects.filter(
                **query_from_request(queryset_self.request, serializer),
            ).order_by(order_field),
        },
    )


def get_objects(model, field_name, field_value):
    """
    Retrieve objects from the specified model that match the given field name and value.

    Args:
        model: The model class.
        field_name (str): The name of the field.
        field_value: The value to match against the field.

    Returns:
        QuerySet: The queryset containing the matching objects.
    """
    return model.objects.filter(**{field_name: field_value})


def save_order(request, order_id):
    """
    Save the order with the specified ID and assign it to the current driver.

    Args:
        request: The HTTP request.
        order_id: The ID of the order to save.
    """
    order = Order.objects.get(id=order_id)
    car_order_qs = CarOrder.objects.filter(models.Q(order=order))
    car_order_qs.delete()
    order.driver = Driver.objects.get(user=request.user)
    order.status = 'executed'
    order.save()


def save_ended_order(order_end_id):
    """
    Save the ended order with the specified ID and update the driver's location.

    Args:
        order_end_id: The ID of the ended order.
    """
    order = Order.objects.get(id=order_end_id)
    car_order_qs = CarOrder.objects.filter(models.Q(order=order))
    car_order_qs.delete()
    order.status = 'evaluation'
    order.save()
    driver = order.driver
    driver.location = order.arrival
    driver.save()


def get_order(request):
    """
    Retrieve the current order associated with the driver.

    Args:
        request: The HTTP request.

    Returns:
        Order: The current order if it exists, otherwise None.
    """
    car_id = Driver.objects.get(user=request.user).car_id
    car = Car.objects.get(id=car_id)
    order = CarOrder.objects.filter(car=car)
    if order:
        return order[0].order
    driver_order = Order.objects.filter(driver__user=request.user, status='executed')
    if driver_order:
        return driver_order[0]


def handle_customer_response(request):
    """
    Handle processing of customer responses to order-related actions.

    Args:
        request: The HTTP request.

    Returns:
        Callable: Redirect to profile.
    """
    if request.POST.get('answer') == 'Cancel order':
        order_id = request.POST.get('order_id')
        Order.objects.filter(customer__user=request.user, id=order_id).delete()
        return redirect(PROFILE_URL)


def query_from_request(request, cls_serializer=None) -> dict:
    """
    Extract query parameters from the request.

    Args:
        request: The HTTP request.
        cls_serializer: The serializer class to extract fields from.

    Returns:
        dict: The extracted query parameters as a dictionary.
    """
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET
