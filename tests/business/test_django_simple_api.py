import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from simple_django_api.jwt.auth import genereate_token


class PermissionTestCase(TestCase):
    def test_basic_auth_required(self):
        response = self.client.get('/basic_auth')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'basic_auth required')

        response = self.client.get('/basic_auth',
                                   HTTP_AUTHORIZATION='Basic: foo')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['msg'], 'hello world')

    def test_jwt(self):
        response = self.client.get('/auth')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['username'], None)

        # non bearer auth
        response = self.client.get('/auth', HTTP_AUTHORIZATION='adasdadsa')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['username'], None)

        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION='Bearer adasdadsa')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'Error decoding signature.')

        User = get_user_model()
        user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                        'johnpassword')
        token = genereate_token(user)
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['username'], 'john')

        new_token = token + 'some_data'
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {new_token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'Error decoding signature.')

        time.sleep(60 * settings.API_JWT_EXPIRATION_MINUTES + 1)
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'Signature has expired.')
