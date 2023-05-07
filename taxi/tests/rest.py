from time import sleep

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.test.client import Client
from rest_framework import status
from rest_framework.test import APIClient
import json

from taxi_manager.models import Car, Driver, Customer, Order, CarOrder

customer_request_content = {
    "user": {"username": "test_user", "password": "23", "first_name": "test", "last_name": "test",
             "email": "123@gmail.com"}, "phone": "12300000001"}
customer_to_change = {"user": {"username": "test_user", "password": "23", "first_name": "test", "last_name": "test",
                               "email": "123@gmail.com"}, "phone": "12300000000"}


def create_viewset_tests(url, cls_model, request_content, to_change):
    class ViewSetTests(TestCase):

        def setUp(self):
            self.client = Client()
            self.creds_user = {'username': 'username', 'password': 'password'}
            self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
            self.user = User.objects.create_user(**self.creds_user)
            self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
            self.token = Token.objects.create(user=self.superuser)

        def test_get(self):
            # logging in with user
            self.client.login(**self.creds_user)
            resp_get = self.client.get(url)
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

            # logging out
            self.client.logout()

        # def manage(self, headers=None):
        #     # POST
        #     resp_post = self.client.post(url, request_content, format='json')
        #     self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        #
        #     # PUT
        #     created = cls_model.objects.get(**request_content)
        #     url_to_created = f'{url}?id={created.id}'
        #     resp_put = self.client.put(url_to_created, data=json.dumps(to_change), headers=headers)
        #     self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        #     attr, attr_value = list(to_change.items())[0]
        #     after_put = cls_model.objects.get(id=created.id)
        #     self.assertEqual(getattr(after_put, attr), attr_value)
        #
        #     # DELETE EXISTING
        #     resp_delete = self.client.delete(url_to_created)
        #     self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
        #
        #     # DELETE NONEXISTENT
        #     resp_delete = self.client.delete(url_to_created)
        #     self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)

        def test_manage_superuser(self):
            # logging in with user
            self.client.login(**self.creds_superuser)

            # self.manage()
            # POST
            resp_post = self.client.post(url, request_content, format='json')
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)

            # PUT
            created = cls_model.objects.get(**request_content)
            url_to_created = f'{url}?id={created.id}'
            resp_put = self.client.put(url_to_created, data=json.dumps(to_change))
            self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
            attr, attr_value = list(to_change.items())[0]
            after_put = cls_model.objects.get(id=created.id)
            self.assertEqual(getattr(after_put, attr), attr_value)

            # DELETE EXISTING
            resp_delete = self.client.delete(url_to_created)
            self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)

            # DELETE NONEXISTENT
            resp_delete = self.client.delete(url_to_created)
            self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)
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
            new_data = request_content.copy()
            if cls_model.__name__ == 'Customer':
                user_data = new_data.pop('user')
                new_user = User.objects.create_user(**user_data)
                new_data['user_id'] = new_user.id

            # POST
            resp_post = self.client.post(url, data=new_data)
            self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)
            # PUT
            created = cls_model.objects.create(**new_data)
            url_to_created = f'{url}?id={created.id}'
            resp_put = self.client.put(url_to_created, data=to_change)
            self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)

            # DELETE EXISTING
            resp_delete = self.client.delete(url_to_created)
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)

            # clean up
            created.delete()

            # logging out
            self.client.logout()

    return ViewSetTests


car_request_content = {'manufacturer': 'test', 'capacity': 4, 'number': '123', 'mark': '123', 'rate': 'economy'}
car_to_change = {'manufacturer': 'test', 'capacity': 5, 'number': '123', 'mark': '123', 'rate': 'economy'}
CarViewSetTests = create_viewset_tests('/rest/Car/', Car, car_request_content, car_to_change)

driver_request_content = {"user": {"username": "test_user", "password": "23", "first_name": "test", "last_name": "test", "email": "123@gmail.com"}, "phone": "12300000000", "car": {"manufacturer": "123", "capacity": "5", "number": "123", "mark": "123", "rate": "economy"}}
driver_to_change = {"user": {"username": "test_user", "password": "23", "first_name": "test", "last_name": "test", "email": "123@gmail.com"}, "phone": "12300000001", "car": {"manufacturer": "123", "capacity": "5", "number": "123", "mark": "123", "rate": "economy"}}
DriverViewSetTests = create_viewset_tests('/rest/Driver/', Driver,
                                          driver_request_content,
                                          driver_to_change)

# CustomerViewSetTests = create_viewset_tests('/rest/Customer/', Customer, customer_request_content, customer_to_change)
#
# order_request_content = {
#     "rating": 4,
#     "departure": "12,12",
#     "arrival": "12,13",
#     "cost": 10.00,
#     "rate": "economy"
# }
# order_to_change = {
#     "rating": 4,
#     "departure": "12,12",
#     "arrival": "12,13",
#     "cost": 12.00,
#     "rate": "economy"
# }
# OrderViewSetTests = create_viewset_tests('/rest/Order/', Order, order_request_content, order_to_change)
