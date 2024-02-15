from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class UserAdmin(UserAdmin):
    model = User
    list_display_links = ["email"]
    search_fields = ("email",)
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_superuser")
    list_filter = ("email", "is_staff", "is_superuser")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": ("is_staff", "is_superuser"),
            },
        ),
    )


admin.site.register(User, UserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "is_active", "loyalty", "count"]


admin.site.register(Profile, ProfileAdmin)
