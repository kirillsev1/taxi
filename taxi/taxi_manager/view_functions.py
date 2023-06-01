from django.db import models
from django.shortcuts import redirect
from rest_framework import viewsets

from taxi_manager.models import Car, CarOrder, Driver, Order

PROFILE_URL = '/profile/'


def create_viewset(cls_model: models.Model, serializer, permission, order_field='id'):
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
    return model.objects.filter(**{field_name: field_value})


def save_order(request, order_id):
    order = Order.objects.get(id=order_id)
    car_order_qs = CarOrder.objects.filter(models.Q(order=order))
    car_order_qs.delete()
    order.driver = Driver.objects.get(user=request.user)
    order.status = 'executed'
    order.save()


def save_ended_order(order_end_id):
    order = Order.objects.get(id=order_end_id)
    car_order_qs = CarOrder.objects.filter(models.Q(order=order))
    car_order_qs.delete()
    order.status = 'evaluation'
    order.save()
    driver = order.driver
    driver.location = order.arrival
    driver.save()


def get_order(request):
    car_id = Driver.objects.get(user=request.user).car_id
    car = Car.objects.get(id=car_id)
    order = CarOrder.objects.filter(car=car)
    if order:
        return order[0].order
    driver_order = Order.objects.filter(driver__user=request.user, status='executed')
    if driver_order:
        return driver_order[0]


def handle_customer_response(request):
    if request.POST.get('answer') == 'Cancel order':
        order_id = request.POST.get('order_id')
        Order.objects.filter(customer__user=request.user, id=order_id).delete()
        return redirect(PROFILE_URL)


def query_from_request(request, cls_serializer=None) -> dict:
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET
