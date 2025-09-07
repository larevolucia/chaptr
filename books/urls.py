""" URL configuration for the books app."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.book_search, name='book_search'),
    path("books/<str:book_id>/", views.book_detail, name="book_detail"),
    path("cover/", views.cover_proxy, name="cover_proxy"),
]
