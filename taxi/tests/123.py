import logging

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.test.client import Client
from rest_framework import status
from rest_framework.test import APIClient
import json

from taxi_manager.models import Car, Driver


car_url = '/rest/Car/'
car_request_content = {'manufacturer': 'test', 'capacity': 4, 'number': '123', 'mark': '123', 'rate': 'economy'}
car_to_change = {'manufacturer': 'test', 'capacity': 4, 'number': '123', 'mark': '123', 'rate': 'economy'}


class CarViewSetTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.creds_user = {'username': 'user', 'password': 'user'}
        self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
        self.user = User.objects.create_user(**self.creds_user)
        self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
        self.token = Token.objects.create(user=self.superuser)

    def test_get(self):
        # logging in with user
        self.client.login(**self.creds_user)
        resp_get = self.client.get(car_url)
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

        # logging out
        self.client.logout()

    def manage(self, headers=None):
        # POST
        resp_post = self.client.post(car_url, data=car_request_content, headers=headers)
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)

        # PUT
        created = Car.objects.get(**car_request_content)
        url_to_created = f'{car_url}?id={created.id}'
        resp_put = self.client.put(url_to_created, data=json.dumps(car_to_change), headers=headers)
        self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        attr, attr_value = list(car_to_change.items())[0]
        after_put = Car.objects.get(id=created.id)
        self.assertEqual(getattr(after_put, attr), attr_value)

        # DELETE EXISTING
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)

        # DELETE NONEXISTENT
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_superuser(self):
        # logging in with user
        self.client.login(**self.creds_superuser)

        self.manage()

        # logging out
        self.client.logout()

    def test_manage_token(self):
        # logging in with rest_framework APIClient
        # (it can be forcefully authenticated with token)
        self.client = APIClient()

        # token goes brrr
        self.client.force_authenticate(user=self.superuser, token=self.token)

    def test_manage_user(self):
        # logging in with user
        self.client.login(**self.creds_user)

        # POST
        resp_post = self.client.post(car_url, data=car_request_content)
        self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)

        # PUT
        created = Car.objects.create(**car_request_content)
        url_to_created = f'{car_url}?id={created.id}'
        resp_put = self.client.put(url_to_created, data=json.dumps(car_to_change))
        self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)

        # DELETE EXISTING
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)

        # clean up
        created.delete()

        # logging out
        self.client.logout()


driver_url = '/rest/Driver/'
driver_request_content = {'user': {'username': 'test',
                                   'password': 'test',
                                   'first_name': 'test',
                                   'last_name': 'test',
                                   'email': 'test@test.ru'},
                          'phone': '+70000000000'}
driver_to_change = {'phone': '+70000000001'}
user_to_create = driver_request_content.pop('user')

class DriverViewSetTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.creds_user = user_to_create if user_to_create else {'username': 'username', 'password': '123'}
        self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
        self.user = User.objects.create_user(**self.creds_user)
        driver_request_content['user'] = User.objects.get_by_natural_key(user_to_create['username'])
        self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
        self.token = Token.objects.create(user=self.superuser)

    def test_get(self):
        # logging in with user
        self.client.login(**self.creds_user)
        resp_get = self.client.get(driver_url)
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

        # logging out
        self.client.logout()

    def manage(self, headers=None):

        # POST
        resp_post = self.client.post(driver_url, data=driver_request_content, headers=headers)
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)

        # PUT
        created = Driver.objects.get(**driver_request_content)
        url_to_created = f'{driver_url}?id={created.id}'
        resp_put = self.client.put(url_to_created, data=json.dumps(driver_to_change), headers=headers)
        self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        attr, attr_value = list(driver_to_change.items())[0]
        after_put = Driver.objects.get(id=created.id)
        self.assertEqual(getattr(after_put, attr), attr_value)

        # DELETE EXISTING
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)

        # DELETE NONEXISTENT
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_token(self):
        # logging in with rest_framework APIClient
        # (it can be forcefully authenticated with token)
        self.client = APIClient()

        # token goes brrr
        self.client.force_authenticate(user=self.superuser, token=self.token)

    def test_manage_user(self):
        Car.objects.create(**car_request_content)
        car_id = Car.objects.get(**car_request_content).id
        driver_request_content['car_id'] = str(car_id)
        driver_to_change['car_id'] = str(car_id)
        # logging in with user
        self.client.login(**self.creds_user)

        # POST
        resp_post = self.client.post(car_url, data=driver_request_content)
        self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)

        # PUT
        created = Driver.objects.create(**driver_request_content)
        url_to_created = f'{driver_url}?id={created.id}'
        resp_put = self.client.put(url_to_created, data=json.dumps(driver_to_change))
        self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)

        # DELETE EXISTING
        resp_delete = self.client.delete(url_to_created)
        self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)

        # clean up
        created.delete()

        # logging out
        self.client.logout()