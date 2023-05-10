from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient
from taxi_manager.models import Car, Driver, Customer, Order

driver_data = {
    "user": {
        "username": "test_user",
        "password": "23",
        "first_name": "test",
        "last_name": "test",
        "email": "123@gmail.com"
    },
    "phone": "12300000000",
    "car": {
        "manufacturer": "123",
        "capacity": "5",
        "number": "123",
        "mark": "123",
        "rate": "1"
    }
}
driver_to_change = {
    "phone": "5550000000",
}

customer_data = {
    "user": {
        "username": "test_user",
        "password": "23",
        "first_name": "test",
        "last_name": "test",
        "email": "123@gmail.com"
    },
    "phone": "12300000000",
}
customer_to_change = {
    "phone": "5550000000",
}


def create_viewset_tests(url, cls_model, request_data, data_to_change):
    class CustomTests(TestCase):
        def setUp(self):
            self.client = APIClient()
            self.creds_user = {'username': 'username', 'password': 'password'}
            self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
            self.user = User.objects.create_user(**self.creds_user)
            self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
            self.token = Token.objects.create(user=self.superuser)

        def test_get(self):
            # logging in with user
            self.client.login(**self.creds_superuser)
            resp_get = self.client.get(url)
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

            # logging out
            self.client.logout()

        def test_post(self):
            if cls_model.__name__ == 'Order':
                driver_user = User.objects.create_user(username='test', password='123')
                car = Car.objects.create(manufacturer='123', capacity=12)
                driver = Driver.objects.create(user=driver_user, phone='23123', car=car)

                customer_user = User.objects.create_user(username='test12', password='123')
                customer = Customer.objects.create(user=customer_user, phone='23123')
                request_data['customer'] = f"/rest/Customer/{customer.__dict__['id']}/"
                request_data['driver'] = f"/rest/Driver/{driver.__dict__['id']}/"

            self.client.login(**self.creds_user)
            resp_post = self.client.post(url, request_data, format='json')
            self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)
            self.client.logout()

            self.client.login(**self.creds_superuser)
            resp_post = self.client.post(url, request_data, format='json')
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            self.client.logout()

        def get_new_id(self):
            match cls_model.__name__:
                case 'Driver':
                    user = User.objects.create_user(username='test', password='123')
                    car = Car.objects.create(manufacturer='123', capacity=12)
                    cls_model.objects.create(user=user, phone='23123', car=car)
                    cls_id = str(cls_model.objects.get(user=user).id)
                case 'Customer':
                    user = User.objects.create_user(username='test', password='123')
                    cls_model.objects.create(user=user, phone='23123')
                    cls_id = str(cls_model.objects.get(user=user).id)
                case 'Order':
                    driver_user = User.objects.create_user(username='test', password='123')
                    car = Car.objects.create(manufacturer='123', capacity=12)
                    driver = Driver.objects.create(user=driver_user, phone='23123', car=car)

                    customer_user = User.objects.create_user(username='test12', password='123')
                    customer = Customer.objects.create(user=customer_user, phone='23123')
                    cls_model.objects.create(driver=driver, customer=customer, rating=4,
                                             order_date=request_data['order_date'])
                    cls_id = str(cls_model.objects.get(driver=driver, customer=customer).id)
                case 'Car':
                    cls_model.objects.create(**request_data)
                    cls_id = cls_model.objects.get(**request_data).id

            return cls_id

        def test_put(self):
            cls_id = self.get_new_id()

            self.client.login(**self.creds_user)
            resp_put = self.client.put(f'{url}?id={cls_id}', data_to_change, format='json')
            self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
            self.client.logout()

            self.client.login(**self.creds_superuser)
            resp_put = self.client.put(f'{url}?id={cls_id}', data_to_change, format='json')
            self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
            resp_get = self.client.get(f'{url}?id={cls_id}')
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
            field = list(data_to_change.keys())[-1]
            self.assertEqual(resp_get.data['results'][0][field], data_to_change[field])
            self.client.logout()

        def test_delete(self):
            cls_id = self.get_new_id()

            self.client.login(**self.creds_user)
            resp_delete = self.client.delete(f'{url}?id={cls_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)
            resp_delete = self.client.delete(f'{url}?id={cls_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)
            self.client.logout()

            self.client.login(**self.creds_superuser)
            resp_delete = self.client.delete(f'{url}?id={cls_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
            resp_delete = self.client.delete(f'{url}?id={cls_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_404_NOT_FOUND)
            self.client.logout()

    return CustomTests


car_request_content = {'manufacturer': 'test', 'capacity': 4, 'number': '123', 'mark': '123', 'rate': '1'}
car_to_change = {'capacity': 5}
order_data = {
    "created": "2023-04-27T10:58:34.703593Z",
    "rating": "5.0",
    "departure": "SRID=4326;POINT (-0.0460052490234375 0.0006866455077859)",
    "order_date": "2023-10-27 0:58:34.703609Z",
    "arrival": "SRID=4326;POINT (-0.0326156616210938 0.0470352120022418)",
    "cost": "0.00",
    "rate": "1",
    "status": "active"
}
order_to_change = {
    "rating": "4.0"
}
DriverViewSetTests = create_viewset_tests('/rest/Driver/', Driver, driver_data, driver_to_change)
CustomerViewSetTests = create_viewset_tests('/rest/Customer/', Customer, customer_data, customer_to_change)
CarViewSetTests = create_viewset_tests('/rest/Car/', Car, car_request_content, car_to_change)
OrderViewSetTests = create_viewset_tests('/rest/Order/', Order, order_data, order_to_change)
