"""Represents the user's reading status for a book."""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()


# Create your models here.
class ReadingStatus(models.Model):
    """Represents the user's reading status for a book."""
    class Status(models.TextChoices):
        """Status choices for the reading status."""
        TO_READ = "TO_READ", "To read"
        READING = "READING", "Reading"
        READ = "READ", "Read"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_statuses"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reading_statuses"
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.TO_READ
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the ReadingStatus model."""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_status'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'book']),
            models.Index(fields=['status']),
        ]
        verbose_name = "Reading status"
        verbose_name_plural = "Reading statuses"


class Rating(models.Model):
    """Stores a user's rating for a book."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    rating = models.PositiveSmallIntegerField(
        default=0,
        help_text="Rating from 0 to 5"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Rating model."""
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="uniq_user_book_rating"
                ),
        ]
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
