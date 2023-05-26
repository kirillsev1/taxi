from django.test import TestCase
from taxi_manager.forms import DriverRegistrationForm, CustomerRegistrationForm, OrderFrom


class TestForms(TestCase):
    def test_driver_registration_form_valid_data(self):
        form = DriverRegistrationForm(data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+71234567890',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'created': '2021-01-01',
            'manufacturer': 'Test Manufacturer',
            'capacity': 4,
            'number': '1234',
            'mark': 'Test Mark',
            'rate': '1'
        })

        self.assertTrue(form.is_valid())

    def test_customer_registration_form_valid_data(self):
        form = CustomerRegistrationForm(data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+71234567890',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })

        self.assertTrue(form.is_valid())

    def test_order_form_valid_data(self):
        form = OrderFrom(data={
            'departure': '55.7558,37.6173',
            'arrival': '55.7592,37.6195',
            'rate': '1'
        })

        self.assertTrue(form.is_valid())

    def test_driver_registration_form_passwords_not_matching(self):
        form = DriverRegistrationForm(data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+71234567890',
            'password1': 'testpassword1',
            'password2': 'testpassword2',
            'created': '2021-01-01',
            'manufacturer': 'Test Manufacturer',
            'capacity': 4,
            'number': '1234',
            'mark': 'Test Mark',
            'rate': '1'
        })

        self.assertEqual(form.errors, 'passwords are different')

    def test_driver_registration_form_wrong_phone(self):
        form = DriverRegistrationForm(data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '4567890',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'created': '2021-01-01',
            'manufacturer': 'Test Manufacturer',
            'capacity': 4,
            'number': '1234',
            'mark': 'Test Mark',
            'rate': '1'
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form, 'wrong phone')
