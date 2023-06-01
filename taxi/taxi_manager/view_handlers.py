from django.db.utils import IntegrityError
from django.shortcuts import redirect

from taxi_manager.forms import EvaluationForm
from taxi_manager.models import CarOrder, Order
from taxi_manager.view_functions import get_objects, save_ended_order, save_order

DRIVER_ORDER_URL = '/driver_order/'
PROFILE_URL = '/profile/'
car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)


def handle_eval_form(request):
    evaluation_form = EvaluationForm(request.POST)
    if evaluation_form.is_valid():
        try:
            evaluation_form.save(request.POST.get('order_id'))
        except IntegrityError:
            return redirect(PROFILE_URL)
        return redirect(PROFILE_URL)


def handle_driver_data(driver, user_data):
    driver_instance = driver[0]
    user_data.update({
        'car': driver_instance.car,
        'driver_phone': driver_instance.phone,
        'orders': list(get_objects(Order, 'driver', driver_instance).order_by('-order_date')),
    })


def handle_customer_data(customer, user_data):
    customer_instance = customer[0]
    user_data.update({
        'orders': list(get_objects(Order, 'customer', customer_instance).order_by('-order_date')),
        'customer_phone': customer_instance.phone,
        'rate_form': EvaluationForm(),
        'car_choices': car_choices,
    })


def handle_driver_resp(request, order_id, driver_response):
    if order_id:
        if driver_response == 'Accept order':
            save_order(request, order_id)
            return redirect(DRIVER_ORDER_URL)
        elif driver_response == 'Cancel':
            current_order = CarOrder.objects.filter(car__driver__user=request.user, order_id=order_id)
            current_order.delete()
        elif driver_response == 'End of trip':
            save_ended_order(order_id)
            return redirect(PROFILE_URL)
