"""Test forms."""
from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.test import TestCase

from taxi_manager.forms import CustomerRegistrationForm, DriverRegistrationForm, OrderFrom
from taxi_manager.models import Customer
from taxi.config import NUMBER_ERROR, NO_DRIVERS_ERROR


class TestForms(TestCase):
    """Test case class for testing forms in the taxi manager application."""

    driver_data = {
        'username': 'testuser',
        'first_name': 'Test1',
        'last_name': 'User1',
        'email': 'test@test.com',
        'phone': '+712345678900',
        'password1': 'test_password',
        'password2': 'test_password',
        'created': '2021-01-01',
        'manufacturer': 'Test Manufacturer',
        'capacity': 4,
        'number': '1234',
        'mark': 'Test Mark',
        'rate': '2',
    }
    user_data = {'username': 'test', 'password': 'testpassword'}
    order_data = {
        'departure': '55.7558,37.6173',
        'arrival': '55.7592,37.6195',
        'rate': '1',
    }

    def test_driver_registration_form_valid_data(self):
        """Test the driver registration form with valid data."""
        form = DriverRegistrationForm(data=self.driver_data)
        self.assertTrue(form.is_valid())

    def test_customer_registration_form_valid_data(self):
        """Test the customer registration form with valid data."""
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
        """Test the order form with valid data."""
        form = OrderFrom(data=self.order_data)
        self.assertTrue(form.is_valid())
        user = User.objects.create_user(**self.user_data)
        Customer.objects.create(user=user, phone='+700000000')
        request = MagicMock()
        request.user = user
        self.assertEqual(form.save(request), NO_DRIVERS_ERROR)

    def test_driver_registration_form_wrong_phone(self):
        """Test the driver registration form with an invalid phone number."""
        form = DriverRegistrationForm(data=self.driver_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save('1.1,1.1'), NUMBER_ERROR)

    def test_order_form_invalid_departure(self):
        """Test the order form with an invalid departure coordinates."""
        form = OrderFrom(data=self.order_data)
        user = User.objects.create_user(**self.user_data)
        Customer.objects.create(user=user, phone='+700000000')
        request = MagicMock()
        request.user = user
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save(request), NO_DRIVERS_ERROR)

    def test_order_form_invalid_arrival(self):
        """Test the order form with an invalid arrival coordinates."""
        form = OrderFrom(data=self.order_data)
        user = User.objects.create_user(**self.user_data)
        Customer.objects.create(user=user, phone='+700000000')
        request = MagicMock()
        request.user = user
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save(request), NO_DRIVERS_ERROR)
