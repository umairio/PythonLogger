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
        ip = self.middleware.get_client_ip(resp.wsgi_request)
        for _ in range(10):
            response = self.middleware(resp.wsgi_request)
        
        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 10)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 11)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_silver_user(self):
        user = User.objects.create_superuser(email='test@example.com', username='testuser', password='password',loyalty='silver')
        client = Client()
        client.force_login(user)
        resp = client.get('/')
        ip = self.middleware.get_client_ip(resp.wsgi_request)

        for _ in range(5):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 5)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 6)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_bronze_user(self):
        user = User.objects.create_superuser(email='test@example.com', username='testuser', password='password',loyalty='bronze')
        client = Client()
        client.force_login(user)
        resp = client.get('/')
        ip = self.middleware.get_client_ip(resp.wsgi_request)
        for _ in range(2):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 2)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 3)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_unauthenticated_user(self):
        client = Client()
        resp = client.get('/')
        ip = self.middleware.get_client_ip(resp.wsgi_request)
        response = self.middleware(resp.wsgi_request)
        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 1)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 2)
        self.assertIsInstance(response, HttpResponseForbidden)