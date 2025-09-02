""" URLs for activity app"""
from django.urls import path
from . import views

urlpatterns = [
    path(
        "books/<str:book_id>/status/",
        views.set_reading_status,
        name="set_reading_status"
    ),
    path(
        "books/<str:book_id>/rating/",
        views.add_rating,
        name="set_rating"
    ),
    path(
        "books/<str:book_id>/review/",
        views.add_review,
        name="add_review"
    ),
    path(
        "books/<str:book_id>/reviews/<int:review_id>/delete/",
        views.delete_review,
        name="delete_review",
    ),
]
