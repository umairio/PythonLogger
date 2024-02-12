from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.test.client import Client
from .middleware.lrmw import LogRequestMiddleware
from django.http import HttpResponseForbidden

User = get_user_model()


class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='password',
            loyalty='gold'
        )

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.loyalty, 'gold')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpassword'
        )

        self.assertIsInstance(superuser, User)
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.username, 'admin')
        self.assertTrue(superuser.check_password('adminpassword'))
        self.assertEqual(superuser.loyalty, 'unauthenticated')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class LogRequestMiddlewaretestCase(TestCase):
    def setUp(self):
        self.middleware = LogRequestMiddleware(lambda r: None)
        self.factory = RequestFactory()

    def test_authenticated_gold_user(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            username="testuser",
            password="password",
            loyalty="gold",
        )
        client = Client()
        client.force_login(user)
        resp = client.get("/")
        ip = self.middleware.get_client_ip(resp.wsgi_request)
        for _ in range(10):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 10)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 11)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_silver_user(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            username="testuser",
            password="password",
            loyalty="silver",
        )
        client = Client()
        client.force_login(user)
        resp = client.get("/")
        ip = self.middleware.get_client_ip(resp.wsgi_request)

        for _ in range(5):
            response = self.middleware(resp.wsgi_request)

        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 5)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 6)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_authenticated_bronze_user(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            username="testuser",
            password="password",
            loyalty="bronze",
        )
        client = Client()
        client.force_login(user)
        resp = client.get("/")
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
        resp = client.get("/")
        ip = self.middleware.get_client_ip(resp.wsgi_request)
        response = self.middleware(resp.wsgi_request)
        self.assertIsNone(response)
        self.assertEqual(len(self.middleware.userlog[ip]), 1)

        response = self.middleware(resp.wsgi_request)
        self.assertEqual(len(self.middleware.userlog[ip]), 2)
        self.assertIsInstance(response, HttpResponseForbidden)
