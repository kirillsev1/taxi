"""Test module for the taxi_manager rest."""
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from taxi_manager.models import Car, Customer, Driver, Order

from taxi.config import (
    CAR_REST_URL,
    CUSTOMER_REST_URL,
    DRIVER_REST_URL,
    ORDER_REST_URL,
)


def create_driver(cls_model, user_data, number_of_seats):
    """
    Create a driver instance with the provided user data and car details.

    Args:
        cls_model (class): The driver model class.
        user_data (dict): User data for creating the driver user.
        number_of_seats (int): Number of seats for the driver's car.

    Returns:
        str: The ID of the created driver instance.
    """
    user = User.objects.create_user(**user_data)
    car = Car.objects.create(manufacturer='23', capacity=number_of_seats)
    cls_model.objects.create(user=user, phone='2313', car=car)
    return str(cls_model.objects.get(user=user).id)


def create_customer(cls_model, user_data):
    """
    Create a customer instance with the provided user data.

    Args:
        cls_model (class): The customer model class.
        user_data (dict): User data for creating the customer user.

    Returns:
        str: The ID of the created customer instance.
    """
    user = User.objects.create_user(**user_data)
    cls_model.objects.create(user=user, phone='23123')
    return str(cls_model.objects.get(user=user).id)


def create_order(cls_model, user_data, number_of_seats, request_data):
    """
    Create an order instance with the provided user data, car details, and request data.

    Args:
        cls_model (class): The order model class.
        user_data (dict): User data for creating the driver and customer users.
        number_of_seats (int): Number of seats for the driver's car.
        request_data (dict): Data for creating the order.

    Returns:
        str: The ID of the created order instance.
    """
    driver_user = User.objects.create_user(**user_data)
    car = Car.objects.create(manufacturer='123', capacity=number_of_seats)
    driver = Driver.objects.create(user=driver_user, phone='23123', car=car)

    user_data['username'] = 'test3'
    customer_user = User.objects.create_user(**user_data)
    customer = Customer.objects.create(user=customer_user, phone='23123')
    cls_model.objects.create(
        driver=driver,
        customer=customer,
        rating=4,
        order_date=request_data['order_date'],
    )
    return str(cls_model.objects.get(driver=driver, customer=customer).id)


def create_car(cls_model, request_data):
    """
    Create a car instance with the provided request data.

    Args:
        cls_model (class): The car model class.
        request_data (dict): Data for creating the car.

    Returns:
        str: The ID of the created car instance.
    """
    cls_model.objects.create(**request_data)
    return str(cls_model.objects.get(**request_data).id)


def create_order_data(password):
    """
    Create driver and customer instances for testing order creation.

    Args:
        password (str): The password for the driver and customer users.

    Returns:
        tuple: A tuple containing the driver and customer instances.
    """
    driver_user = User.objects.create_user(username='test', password=password)
    car = Car.objects.create(manufacturer='123', capacity=4)
    driver = Driver.objects.create(user=driver_user, phone='2123', car=car)

    customer_user = User.objects.create_user(username='test1', password=password)
    customer = Customer.objects.create(user=customer_user, phone='2313')

    return driver, customer


def create_view_set_tests(url, cls_model, request_data, data_to_change):
    """
    Create test cases for a REST API viewset.

    Args:
        url (str): The URL endpoint for the viewset.
        cls_model (class): The model class associated with the viewset.
        request_data (dict): Data for creating an instance of the model.
        data_to_change (dict): Data for changing an instance of the model.

    Returns:
        class: The custom test case class.
    """

    class CustomTestCase(TestCase):
        """Custom test case class for testing REST API viewsets."""

        def setUp(self):
            """Set up the necessary data for test cases."""
            self.client = APIClient()
            self.creds_user = {'username': 'username', 'password': 'password'}
            self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
            self.user = User.objects.create_user(**self.creds_user)
            self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
            self.token = Token.objects.create(user=self.superuser)

        def test_get(self):
            """Test the GET request for the viewset."""
            self.client.login(**self.creds_superuser)
            resp_get = self.client.get(url)
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

            self.client.logout()

        def test_post(self):
            """Test the POST request for the viewset."""
            if cls_model.__name__ == 'Order':
                driver, customer = create_order_data(self.creds_user.get('password'))
                request_data['customer'] = '/rest/customer/{0}/'.format(customer.id)
                request_data['driver'] = '/rest/driver/{0}/'.format(driver.id)

            self.client.login(**self.creds_superuser)
            resp_post = self.client.post(url, request_data, format='json')
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED, resp_post.content)
            self.client.logout()

        def get_new_id(self):
            """
            Get the ID of a newly created instance.

            Returns:
                str: The ID of the newly created instance.
            """
            cls_id = None
            user_data = {'username': 'test', 'password': '123'}
            number_of_seats = 4
            if cls_model.__name__ == 'Driver':
                cls_id = create_driver(cls_model, user_data, number_of_seats)
            elif cls_model.__name__ == 'Customer':
                cls_id = create_customer(cls_model, user_data)
            elif cls_model.__name__ == 'Order':
                cls_id = create_order(cls_model, user_data, number_of_seats, request_data)
            elif cls_model.__name__ == 'Car':
                cls_id = create_car(cls_model, request_data)
            return cls_id

        def test_patch(self):
            """Test the PATCH request for the viewset."""
            cls_id = self.get_new_id()

            self.client.login(**self.creds_superuser)
            resp_patch = self.client.patch(
                '{0}{1}/'.format(url, cls_id),
                data_to_change,
                format='json',
            )

            self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
            resp_get = self.client.get('{0}{1}/'.format(url, cls_id))
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
            self.client.logout()

        def test_failed_patch(self):
            """Test a failed PATCH request for the viewset."""
            cls_id = self.get_new_id()

            self.client.login(**self.creds_user)
            resp_patch = self.client.patch(
                '{0}{1}/'.format(url, cls_id),
                data_to_change,
                format='json',
            )
            self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
            self.client.logout()

        def test_delete(self):
            """Test the DELETE request for the viewset."""
            cls_id = self.get_new_id()

            self.client.login(**self.creds_user)
            resp_delete = self.client.delete('{0}{1}/'.format(url, cls_id))
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)
            self.client.logout()

            self.client.login(**self.creds_superuser)
            resp_delete = self.client.delete('{0}{1}/'.format(url, cls_id))
            self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
            resp_delete = self.client.delete('{0}{1}/'.format(url, cls_id))
            self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)
            self.client.logout()

    return CustomTestCase


car_request_content = {'manufacturer': 'test', 'capacity': 4, 'number': '125', 'mark': '153', 'rate': '1'}
car_to_change = {'capacity': 5}
order_data = {
    'created': '2023-04-27T10:58:34.703593Z',
    'rating': '5.0',
    'departure': 'SRID=4326;POINT (-0.0460052490234375 0.0006866455077859)',
    'order_date': '2023-10-27 0:58:34.703609Z',
    'arrival': 'SRID=4326;POINT (-0.0326156616210938 0.0470352120022418)',
    'cost': '0.00',
    'rate': '1',
    'status': 'active',
}
order_to_change = {
    'rating': '4.0',
}

driver_data = {
    'user': {
        'username': 'tsst',
        'password': '23',
        'first_name': 'test',
        'last_name': 'test',
        'email': '123@gmail.com',
    },
    'phone': '31243123541',
    'car': {
        'manufacturer': '163',
        'capacity': '5',
        'number': '223',
        'mark': '423',
        'rate': '1',
    },
}

phone_to_change = {
    'phone': '5550000000',
}

customer_data = {
    'user': {
        'username': 'test_user',
        'password': '23',
        'first_name': 'tsst',
        'last_name': 'trst',
        'email': '13@gmail.com',
    },
    'phone': '1200000000',
}

DriverViewSetTests = create_view_set_tests(DRIVER_REST_URL, Driver, driver_data, phone_to_change)
CustomerViewSetTests = create_view_set_tests(CUSTOMER_REST_URL, Customer, customer_data, phone_to_change)
CarViewSetTests = create_view_set_tests(CAR_REST_URL, Car, car_request_content, car_to_change)
OrderViewSetTests = create_view_set_tests(ORDER_REST_URL, Order, order_data, order_to_change)
