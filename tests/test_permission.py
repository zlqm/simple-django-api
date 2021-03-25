from django.test import TestCase


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

    def test_owner_required(self):
        response = self.client.get('/blogs/2')
        resp_data = response.json()
        self.assertEqual(resp_data['detail'], 'not owner')

        response = self.client.get('/blogs/1')
        resp_data = response.json()
        self.assertEqual(resp_data['pk'], 1)
