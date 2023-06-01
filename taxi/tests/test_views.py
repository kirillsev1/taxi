from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from rest_framework import status

from taxi_manager.models import Car, Customer, Driver
from taxi.config import PROFILE_URL, CUSTOMER_ORDER_URL, DRIVER_ORDER_URL

car = {
    'manufacturer': '123',
    'capacity': '5',
    'number': '123',
    'mark': '123',
    'rate': '1',
}


class SetUpMixin(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_data = {'username': 'test_customer', 'password': 'test_customer'}
        customer_user = User.objects.create_user(**self.customer_data)
        self.customer = Customer.objects.create(user=customer_user, phone='+7000000000')

        self.driver_data = {'username': 'test_driver', 'password': 'test_driver'}
        driver_user = User.objects.create_user(**self.driver_data)
        driver_car = Car.objects.create(**car)
        self.driver = Driver.objects.create(user=driver_user, car=driver_car, phone='+7000000000')


class DriverPageTest(SetUpMixin):
    url = DRIVER_ORDER_URL

    def test_driver_view(self):
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_302_FOUND)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)


class CustomerPageTest(SetUpMixin):
    url = CUSTOMER_ORDER_URL

    def test_driver_view(self):
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_302_FOUND)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)


class IndexPageTest(SetUpMixin):
    url = '/'

    def test_page(self):
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
    url = PROFILE_URL

    def test_driver_view(self):
        self.client.login(**self.driver_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)

    def test_customer_view(self):
        self.client.login(**self.customer_data)
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, status.HTTP_200_OK)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)
