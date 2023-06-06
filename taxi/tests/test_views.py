"""Test module for the taxi_manager views."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from rest_framework import status
from taxi_manager.models import Car, Customer, Driver

from taxi.config import CUSTOMER_ORDER_URL, DRIVER_ORDER_URL, PROFILE_URL

car = {
    'manufacturer': '123',
    'capacity': '5',
    'number': '123',
    'mark': '123',
    'rate': '1',
}


class SetUpMixin(TestCase):
    """A mixin class for setting up data for test cases."""

    def setUp(self):
        """Set up the necessary data for test cases."""
        self.client = Client()
        self.customer_data = {'username': 'test_customer', 'password': 'test_customer'}
        customer_user = User.objects.create_user(**self.customer_data)
        self.customer = Customer.objects.create(user=customer_user, phone='+7000000000')

        self.driver_data = {'username': 'test_driver', 'password': 'test_driver'}
        driver_user = User.objects.create_user(**self.driver_data)
        driver_car = Car.objects.create(**car)
        self.driver = Driver.objects.create(user=driver_user, car=driver_car, phone='+7000000000')


class DriverPageTest(SetUpMixin):
    """Test cases for the driver view."""

    url = DRIVER_ORDER_URL

    def test_driver_view(self):
        """Test the driver view."""
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        """Test the customer view from the driver perspective."""
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_302_FOUND)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)


class CustomerPageTest(SetUpMixin):
    """Test cases for the customer view."""

    url = CUSTOMER_ORDER_URL

    def test_driver_view(self):
        """Test the driver view from the customer perspective."""
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_302_FOUND)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        """Test the customer view."""
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)


class IndexPageTest(SetUpMixin):
    """Test cases for the index page."""

    url = '/'

    def test_page(self):
        """Test the index page."""
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)


class ProfilePageTest(SetUpMixin):
    """Test cases for the profile page."""

    url = PROFILE_URL

    def test_driver_view(self):
        """Test the profile page from the driver perspective."""
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        """Test the profile page from the customer perspective."""
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)
