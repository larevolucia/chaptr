from django.urls import path
from . import views

urlpatterns = [
    path("books/<str:book_id>/status/", views.set_reading_status, name="set_reading_status"),
]
