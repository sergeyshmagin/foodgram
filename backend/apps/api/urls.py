"""URL configuration for Foodgram API with versioning."""
from django.urls import include, path
from drf_spectacular.views import SpectacularSwaggerView

app_name = "api"

urlpatterns = [
    # Документация API (требование ревьювера)
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:v1:schema"),
        name="docs",
    ),
    # API версии
    path("v1/", include("apps.api.v1.urls", namespace="v1")),
    path("", include("apps.api.v1.urls", namespace="default")),
]
