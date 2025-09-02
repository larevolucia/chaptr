""" library App Configuration """
from django.apps import AppConfig


class LibraryConfig(AppConfig):
    """ Configuration for the library app. """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'
