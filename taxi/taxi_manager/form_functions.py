import datetime
from time import monotonic, sleep

from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D

from taxi_manager.models import Driver, Order
from taxi.config import SRID, NUMBER_LEN, CARS_CREATION_YEAR, car_choices, PASSWORDS_ERROR, NUMBER_ERROR
from taxi.config import GEO_ERROR, CAR_CREATION_ERROR, TIME_ERROR, NO_DRIVERS_ERROR


def check(cleaned_data, location_str=None):
    if cleaned_data.get('password1') != cleaned_data.get('password2'):
        return PASSWORDS_ERROR
    phone = cleaned_data.get('phone')
    if not phone.startswith('+7') or len(phone) != NUMBER_LEN:
        return NUMBER_ERROR
    if location_str is not None:
        if len(location_str.split(',')) != 2:
            return GEO_ERROR
        if cleaned_data.get('created') < datetime.date(*CARS_CREATION_YEAR):
            return CAR_CREATION_ERROR
        if datetime.date.today() < cleaned_data.get('created'):
            return TIME_ERROR


def get_point(points):
    x_pos, y_pos = points.split(',')
    return Point(float(x_pos), float(y_pos), srid=SRID)


def get_objects_by_field(model, field_name, field_value):
    queryset = model.objects.filter(**{field_name: field_value})
    return list(queryset)


def find_available_drivers(order, higher_rates, distance):
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
    return not Order.objects.filter(driver=driver, status='active').exists()


def get_rates(current_rate_index):
    return [car_choices[ind][0] for ind in range(current_rate_index, len(car_choices))]
