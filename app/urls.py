from django.urls import path

from .views import index

urlpatterns = [
    path("", index, name="index"),
    path("home", index, name="index"),
]
