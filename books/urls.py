from django.urls import path
from .views import test_api_key, book_search

urlpatterns = [
    path("test-api-key/", test_api_key),
    path("search/", book_search),
]
