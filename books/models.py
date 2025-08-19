"""Represents a book in the system.

    Returns:
        Model: A Django model representing a book.
"""
from django.db import models
from django.utils import timezone


# Create your models here.
class Book(models.Model):
    """
    A saved book (only created if a user adds it to a shelf / sets status).
    Primary key is the Google volumeId.
    """
    id = models.CharField(primary_key=True, max_length=64)

    # Minimal metadata to show saved items without re-fetching
    title = models.CharField(max_length=512, blank=True)
    authors = models.JSONField(blank=True, null=True)  # list[str]
    thumbnail_url = models.URLField(max_length=500, blank=True)
    language = models.CharField(max_length=16, blank=True)
    published_date_raw = models.CharField(max_length=32, blank=True)

    # (Optional) timestamps for local record keeping only
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Book model."""
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return str(self.title) or str(self.id)
