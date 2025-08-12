from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.book_search, name='book-search'),
    path("books/<str:book_id>/", views.book_detail, name="book_detail"),
]
