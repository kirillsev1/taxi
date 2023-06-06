"""Functions for forms."""
import datetime
from time import monotonic, sleep

from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D

from taxi_manager.models import Driver, Order
from taxi.config import SRID, NUMBER_LEN, CARS_CREATION_YEAR, car_choices, PASSWORDS_ERROR, NUMBER_ERROR
from taxi.config import GEO_ERROR, CAR_CREATION_ERROR, TIME_ERROR, NO_DRIVERS_ERROR


def check(cleaned_data, location_str=None):
    """
    Check the validity of cleaned data and location information.

    Args:
        cleaned_data: The cleaned form data.
        location_str: The location as a string (optional).

    Returns:
        str or None: An error message if there is a validation error, None otherwise.
    """
    if cleaned_data.get('password1') != cleaned_data.get('password2'):
        return PASSWORDS_ERROR
    phone = cleaned_data.get('phone')
    if not phone.startswith('+7') or len(phone) != NUMBER_LEN:
        return NUMBER_ERROR
    if location_str is not None:
        if cleaned_data.get('created') < datetime.date(*CARS_CREATION_YEAR):
            return CAR_CREATION_ERROR
        if datetime.date.today() < cleaned_data.get('created'):
            return TIME_ERROR
    elif len(location_str.split(',')) != 2:
        return GEO_ERROR


def get_point(points):
    """
    Convert a string representation of coordinates to a Point object.

    Args:
        points: The coordinates as a string in the format "x,y".

    Returns:
        Point: The Point object representing the coordinates.
    """
    x_pos, y_pos = points.split(',')
    return Point(float(x_pos), float(y_pos), srid=SRID)


def get_objects_by_field(model, field_name, field_value):
    """
    Get objects of a model based on a specific field.

    Args:
        model: The model class.
        field_name: The name of the field.
        field_value: The value of the field.

    Returns:
        list: A list of objects that match the field criteria.
    """
    queryset = model.objects.filter(**{field_name: field_value})
    return list(queryset)


def find_available_drivers(order, higher_rates, distance):
    """
    Find available drivers for an order based on rate and distance.

    Args:
        order: The order object.
        higher_rates: A list of higher rate options.
        distance: A range of distances to search within.

    Returns:
        list or str: A list of available drivers if found, or an error message if not.
    """
    start = monotonic()
    while True:
        if monotonic() - start >= 10:
            order.delete()
            return NO_DRIVERS_ERROR
        for radius in range(*distance):
            for rate in higher_rates:
                drivers = Driver.objects.filter(
                    location__dwithin=(GEOSGeometry(order.departure), D(m=radius), 90),
                    car__rate=rate,
                )
                if drivers:
                    return drivers
            sleep(1)


def is_order_active(driver):
    """
    Check if an order is active for a driver.

    Args:
        driver: The driver object.

    Returns:
        bool: True if the driver has an active order, False otherwise.
    """
    return not Order.objects.filter(driver=driver, status='active').exists()


def get_rates(current_rate_index):
    """
    Get a list of rates starting from a given index.

    Args:
        current_rate_index: The index to start from.

    Returns:
        list: A list of rates.
    """
    return [car_choices[ind][0] for ind in range(current_rate_index, len(car_choices))]
