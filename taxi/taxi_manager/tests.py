from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Driver, Customer, Car, Order, CarOrder
from .serializers import DriverSerializer, CustomerSerializer, CarSerializer, OrderSerializer, CarOrderSerializer


class DriverTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'test_user',
            'password': 'test_password',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
        self.driver_data = {
            'user': self.user_data,
            'phone': '123456789',
            'car': None
        }
        self.driver = Driver.objects.create(user=User.objects.create_user(**self.user_data), phone='123456789')

    def test_create_driver(self):
        response = self.client.post('/api/drivers/', self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Driver.objects.count(), 2)
        self.assertEqual(Driver.objects.get(id=2).phone, '123456789')

    def test_get_driver(self):
        response = self.client.get(f'/api/drivers/{self.driver.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, DriverSerializer(self.driver).data)

    def test_update_driver(self):
        self.driver_data['phone'] = '987654321'
        response = self.client.put(f'/api/drivers/{self.driver.id}/', self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Driver.objects.get(id=self.driver.id).phone, '987654321')
