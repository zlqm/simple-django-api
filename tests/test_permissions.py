from django.test import TestCase

from django_improved_view import error_code

error_code.OK = 0


class PermissionTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get('/perm-test/')
        resp_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data['error_code'], 10000)
        self.assertEqual(resp_data['hint'], 'basic auth required')
        self.assertEqual(resp_data['data'], {})

        response = self.client.get('/perm-test/',
                                   HTTP_AUTHORIZATION='Basic: asdadsad')
        resp_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data['error_code'], 0)
