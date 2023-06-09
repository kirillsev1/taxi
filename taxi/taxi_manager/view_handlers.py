"""Functions for handles views."""
from django.db.utils import IntegrityError
from django.shortcuts import redirect

from taxi.config import DRIVER_ORDER_URL, PROFILE_URL, car_choices
from taxi_manager.forms import EvaluationForm
from taxi_manager.models import CarOrder, Order
from taxi_manager.view_functions import get_objects, save_ended_order, save_order


def handle_eval_form(request):
    """
    Handle the processing of the evaluation form submission.

    Args:
        request: The HTTP request.

    Returns:
        HttpResponse: The response indicating the success or failure of the form submission.
    """
    evaluation_form = EvaluationForm(request.POST)
    if evaluation_form.is_valid():
        try:
            evaluation_form.save(request.POST.get('order_id'))
        except IntegrityError:
            return redirect(PROFILE_URL)
        return redirect(PROFILE_URL)


def handle_driver_data(driver, user_data):
    """
    Update the user_data dictionary with driver-related information.

    Args:
        driver: The driver instance.
        user_data: The dictionary containing user-related data.
    """
    driver_instance = driver[0]
    user_data.update({
        'car': driver_instance.car,
        'driver_phone': driver_instance.phone,
        'orders': list(get_objects(Order, 'driver', driver_instance).order_by('-order_date')),
    })


def handle_customer_data(customer, user_data):
    """
    Update the user_data dictionary with customer-related information.

    Args:
        customer: The customer instance.
        user_data: The dictionary containing user-related data.
    """
    customer_instance = customer[0]
    user_data.update({
        'orders': list(get_objects(Order, 'customer', customer_instance).order_by('-order_date')),
        'customer_phone': customer_instance.phone,
        'rate_form': EvaluationForm(),
        'car_choices': car_choices,
    })


def handle_driver_resp(request, order_id, driver_response):
    """
    Handle processing of driver responses to order requests.

    Args:
        request: The HTTP request.
        order_id: The ID of the order.
        driver_response: The driver's response to the order request.

    Returns:
        HttpResponseRedirect or None: Redirection to a URL or None if no redirection is needed.
    """
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
