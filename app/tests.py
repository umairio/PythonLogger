from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.test.client import Client 
from .middleware.lrmw import LogRequestMiddleware
from django.http import HttpResponseForbidden

User = get_user_model()

class LogRequestMiddlewaretestCase(TestCase):
    def setUp(self):
        self.middleware = LogRequestMiddleware(lambda r: None)
        self.factory = RequestFactory()

    def test_authenticated_gold_user(self):
        user = User.objects.create_superuser(email='test@example.com', username='testuser', password='password',loyalty='gold')
        client = Client()
        client.force_login(user)
        resp = client.get('/')

        for _ in range(10):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 10)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 11)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_silver_user(self):
        user = User.objects.create_superuser(email='test@example.com', username='testuser', password='password',loyalty='silver')
        client = Client()
        client.force_login(user)
        resp = client.get('/')

        for _ in range(5):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 5)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 6)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_bronze_user(self):
        user = User.objects.create_superuser(email='test@example.com', username='testuser', password='password',loyalty='bronze')
        client = Client()
        client.force_login(user)
        resp = client.get('/')

        for _ in range(2):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 2)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 3)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_unauthenticated_user(self):
        client = Client()
        resp = client.get('/')

        response = self.middleware(resp.wsgi_request)
        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 1)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog['127.0.0.1']), 2)
        self.assertIsInstance(response, HttpResponseForbidden)