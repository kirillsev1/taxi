from http.client import OK
from django.test.client import Client
from django.contrib.auth.models import User
from django.test import TestCase

from taxi_manager.models import Car, Customer, Driver

car = {
    "manufacturer": "123",
    "capacity": "5",
    "number": "123",
    "mark": "123",
    "rate": "1"
}


class SetUpMixin(TestCase):
    def setUp(self):
        self.client = Client()
        customer_user = User.objects.create_user(username='test_customer', password='test_customer')
        self.customer = Customer.objects.create(user=customer_user, phone='+7000000000')

        driver_user = User.objects.create_user(username='test_driver', password='test_driver')
        driver_car = Car.objects.create(**car)
        self.driver = Driver.objects.create(user=driver_user, car=driver_car, phone='+7000000000')


class DriverPageTest(SetUpMixin):
    url = '/driver_order/'

    def test_driver_view(self):
        self.client.login(username='test_driver', password='test_driver')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_customer_view(self):
        self.client.login(username='test_customer', password='test_customer')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 302)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)


class CustomerPageTest(SetUpMixin):
    url = '/customer_order/'

    def test_driver_view(self):
        self.client.login(username='test_driver', password='test_driver')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 302)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_customer_view(self):
        self.client.login(username='test_customer', password='test_customer')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)


class IndexPageTest(SetUpMixin):
    url = '/'

    def test_page(self):
        self.client.login(username='test_customer', password='test_customer')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        self.client.logout()
        self.client.login(username='test_driver', password='test_driver')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 200)


class ProfilePageTest(SetUpMixin):
    url = '/profile/'

    def test_driver_view(self):
        self.client.login(username='test_driver', password='test_driver')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        print(page_resp)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_customer_view(self):
        self.client.login(username='test_customer', password='test_customer')
        page_resp = self.client.get(self.url)
        self.assertEqual(page_resp.status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)
