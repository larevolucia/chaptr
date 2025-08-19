"""Represents a book in the system.

    Returns:
        Model: A Django model representing a book.
"""
from django.db import models
from django.utils import timezone


# Create your models here.
class Book(models.Model):
    """Represents a book in the system.

    Args:
        models (Model): Django model base class.

    Returns:
        Model: A Django model representing a book.
    """
    # Google volumeId is the primary key
    id = models.CharField(primary_key=True, max_length=64)

    # Minimal metadata for quick rendering
    title = models.CharField(max_length=512, blank=True)
    authors = models.JSONField(blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    language = models.CharField(max_length=16, blank=True)
    published_date_raw = models.CharField(max_length=32, blank=True)

    # For caching and avoiding unnecessary API calls
    etag = models.CharField(max_length=128, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_fetched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta options for the Book model."""
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return str(self.title) if self.title else str(self.id)

    def needs_refresh(self, ttl_minutes: int = 1440) -> bool:
        """
        Soft TTL so Google is not called on every page view.
        Returns a boolean value indicating if the book needs to be refreshed.
        """
        age = timezone.now() - (self.last_fetched_at or timezone.now())
        return age.total_seconds() > ttl_minutes * 60
