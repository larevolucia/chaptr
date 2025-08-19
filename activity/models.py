"""Represents the user's reading status for a book."""
from django.conf import settings
from django.db import models
from django.utils import timezone


# Create your models here.
class ReadingStatus(models.Model):
    """Represents the user's reading status for a book."""
    class Status(models.TextChoices):
        """Status choices for the reading status."""
        TO_READ = "TO_READ", "To read"
        READING = "READING", "Reading"
        READ = "READ", "Read"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # noqa: E501 pylint: disable=line-too-long
    book = models.ForeignKey("books.Book", to_field="id", on_delete=models.CASCADE, related_name="reading_statuses")  # noqa: E501 pylint: disable=line-too-long
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TO_READ)  # noqa: E501 pylint: disable=line-too-long
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the ReadingStatus model."""
        unique_together = ("user", "book")
        indexes = [models.Index(fields=["user", "status"]), models.Index(fields=["book"])]  # noqa: E501 pylint: disable=line-too-long
