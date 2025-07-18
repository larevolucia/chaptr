from django.urls import path
from .views import test_api_key

urlpatterns = [
    path("test-api-key/", test_api_key),
]
