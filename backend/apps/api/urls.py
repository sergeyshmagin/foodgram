"""URL configuration for Foodgram API with versioning."""
from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("v1/", include("apps.api.v1.urls", namespace="v1")),
    path("", include("apps.api.v1.urls", namespace="default")),
]
