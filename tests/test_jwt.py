import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from simple_django_api.jwt.auth import generate_token

User = get_user_model()


class JwtTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
            'johnpassword',
        )

    def test_no_auth(self):
        # no auth
        response = self.client.get('/auth')
        self.assertEqual(response.status_code, 401)

    def test_non_bearer_auth(self):
        # non bearer auth
        response = self.client.get('/auth', HTTP_AUTHORIZATION='adasdadsa')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'NO_TOKEN')

    def test_invalid_token(self):
        # invalid token
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION='Bearer adasdadsa')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'DECODE_ERROR')

    def test_valid_token(self):
        # valid token
        token = generate_token(self.__class__.user)
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['username'], 'john')

    def test_broken_token(self):
        token = generate_token(self.__class__.user)
        new_token = token + 'some_data'
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {new_token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'DECODE_ERROR')

    def test_expired_token(self):
        token = generate_token(self.__class__.user)
        time.sleep(60 * settings.API_JWT_EXPIRATION_MINUTES + 1)
        response = self.client.get('/auth',
                                   HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['detail'], 'EXPIRED')
