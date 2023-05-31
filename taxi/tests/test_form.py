from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.test import TestCase

from taxi_manager.forms import CustomerRegistrationForm, DriverRegistrationForm, OrderFrom
from taxi_manager.models import Customer


class TestForms(TestCase):
    driver_data = {
        'username': 'testuser',
        'first_name': 'Test1',
        'last_name': 'User1',
        'email': 'test@test.com',
        'phone': '+71234567890',
        'password1': 'test_password',
        'password2': 'test_password',
        'created': '2021-01-01',
        'manufacturer': 'Test Manufacturer',
        'capacity': 4,
        'number': '1234',
        'mark': 'Test Mark',
        'rate': '2',
    }

    def test_driver_registration_form_valid_data(self):
        form = DriverRegistrationForm(data=self.driver_data)

        self.assertTrue(form.is_valid())

    def test_customer_registration_form_valid_data(self):
        form = CustomerRegistrationForm(data={
            'username': 'testuser',
            'first_name': 'Test2',
            'last_name': 'User2',
            'email': 'test@example.com',
            'phone': '+7123456789',
            'password1': 'testpassword1',
            'password2': 'testpassword1',
        })

        self.assertTrue(form.is_valid())

    def test_order_form_valid_data(self):
        form = OrderFrom(data={
            'departure': '55.7558,37.6173',
            'arrival': '55.7592,37.6195',
            'rate': '1',
        })
        self.assertTrue(form.is_valid())
        user_data = {'username': 'test', 'password': 'testpassword'}
        user = User.objects.create_user(**user_data)
        Customer.objects.create(user=user, phone='+700000000')
        request = MagicMock()
        request.user = user
        self.assertEqual(form.save(request), 'No free drivers behind you')

    def test_driver_registration_form_wrong_phone(self):
        form = DriverRegistrationForm(data=self.driver_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save('1.1,1.1'), 'wrong number')
