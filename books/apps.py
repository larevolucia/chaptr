""" Django app configuration for the books app."""
from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Configuration for the books app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'
