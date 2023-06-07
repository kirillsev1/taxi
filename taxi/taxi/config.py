"""Configuration file."""
car_choices = (
    ('1', 'economy'),
    ('2', 'comfort'),
    ('3', 'business'),
)
order_statuses = (
    ('completed', 'completed'),
    ('active', 'active'),
    ('canceled', 'canceled'),
    ('executed', 'executed'),
    ('evaluation', 'evaluation'),
)

NUMBER_LEN = 12
MAX_STR_LEN = 30
SRID = 4326
RUBLE = 84
STARTING_COST = 75
CARS_CREATION_YEAR = (1885, 1, 29)

PASSWORDS_ERROR = 'passwords are different'
NUMBER_ERROR = 'wrong number'
GEO_ERROR = 'Access your geolocation'
CAR_CREATION_ERROR = 'cars were not created yet'
TIME_ERROR = 'Sorry we can`t travel in time'
NO_DRIVERS_ERROR = 'No free drivers behind you'
USER_ERROR = 'User with such username already exists'
DEPARTURE_COORDS_ERROR = 'Wrong departure coordinates'
ARRIVAL_COORDS_ERROR = 'Wrong arrival coordinates'

ERROR = 'error'
FORM = 'form'
POST = 'POST'
ID_STR = 'id'
USER_STR = 'user'

PROFILE_URL = '/profile/'
LOGIN_URL = '/login/'
DRIVER_ORDER_URL = '/driver_order/'
CUSTOMER_ORDER_URL = '/customer_order/'

REG_TEMPLATE = 'registration/register.html'
ORDER_PAGE_TEMPLATE = 'taxi/order_page.html'
DRIVER_ORDER_TEMPLATE = 'taxi/driver_order.html'
INDEX_TEMPLATE = 'taxi/index.html'
PROFILE_TEMPLATE = 'taxi/profile.html'

DRIVER_REST_URL = '/rest/driver/'
CUSTOMER_REST_URL = '/rest/customer/'
CAR_REST_URL = '/rest/car/'
ORDER_REST_URL = '/rest/order/'
