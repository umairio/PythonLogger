from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_superuser = models.BooleanField(_("superuser status"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Profile(models.Model):
    class Loyalty(models.TextChoices):
        Gold = "gold"
        Silver = "silver"
        Bronze = "bronze"

    user = models.OneToOneField(
        "User", verbose_name=_("user"), on_delete=models.CASCADE
    )
    is_active = models.BooleanField(_("active"), default=True)
    loyalty = models.CharField(
        _("loyalty"),
        max_length=20,
        choices=Loyalty.choices,
        default=Loyalty.Bronze,
    )
    count = models.IntegerField(default=0)
    first_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email
