from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.test import RequestFactory, TestCase
from django.test.client import Client

from app.models import Profile

from .middleware.lrmw import LogRequestMiddleware

User = get_user_model()


class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password",
        )
        profile = Profile.objects.create(user=user, loyalty="gold")

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("password"))
        self.assertEqual(profile.loyalty, "gold")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        profile = Profile.objects.create(user=superuser)

        self.assertIsInstance(superuser, User)
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("adminpassword"))
        self.assertEqual(profile.loyalty, "bronze")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class LogRequestMiddlewaretestCase(TestCase):
    def setUp(self):
        self.middleware = LogRequestMiddleware(lambda r: None)
        self.factory = RequestFactory()

    def test_authenticated_gold_user(self):
        user = User.objects.create_superuser(
            email="gold@example.com",
            password="password",
        )
        profile = Profile.objects.create(user=user, loyalty="gold")
        client = Client()
        client.force_login(user)

        for _ in range(10):
            resp = client.get("/home")
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.count, 10)

        resp = client.get("/home")
        self.assertIsInstance(resp, HttpResponseForbidden)

    def test_authenticated_silver_user(self):
        user = User.objects.create_superuser(
            email="silver@example.com",
            password="password",
        )
        profile = Profile.objects.create(user=user, loyalty="silver")
        client = Client()
        client.force_login(user)

        for _ in range(5):
            resp = client.get("/home")
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.count, 5)

        resp = client.get("/home")
        self.assertIsInstance(resp, HttpResponseForbidden)

    def test_authenticated_bronze_user(self):
        user = User.objects.create_superuser(
            email="bronze@example.com",
            password="password",
        )
        profile = Profile.objects.create(user=user, loyalty="bronze")
        client = Client()
        client.force_login(user)

        for _ in range(2):
            resp = client.get("/home")
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.count, 2)

        resp = client.get("/home")
        self.assertIsInstance(resp, HttpResponseForbidden)

    def test_unauthenticated_user(self):
        client = Client()
        resp = client.get("/home")
        self.assertIsInstance(resp, HttpResponseForbidden)
