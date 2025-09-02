"""Represents the user's reading status for a book."""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
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
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True, editable=False)

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
                name="uniq_user_book_rating",
                condition=Q(is_archived=False)
                ),
        ]
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"


class Review(models.Model):
    """Stores a user's review for a book."""
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Review model."""
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="uniq_user_book_review",
                condition=Q(is_archived=False)
            ),
        ]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
