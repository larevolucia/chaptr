"""
Service for managing reading statuses and rating.
"""
from django.db.models import Avg
from django.utils import timezone
from .models import ReadingStatus, Rating, Review


def statuses_map_for(user, book_ids):
    """
    Returns {book_id: {"status": "..."}}
    """
    if not getattr(user, "is_authenticated", False) or not book_ids:
        return {}
    rows = (
        ReadingStatus.objects
        .filter(user=user, book_id__in=set(book_ids))
        .values("book_id", "status")
    )
    return {r["book_id"]: {"status": r["status"]} for r in rows}


def ratings_map_for(user, ids):
    """Return {book_id: rating} for the given user and list of book IDs."""
    if not getattr(user, "is_authenticated", False) or not ids:
        return {}
    qs = (
        Rating.objects
        .filter(user=user, book_id__in=ids, is_archived=False)
        .only("book_id", "rating")
    )
    return {r.book_id: r.rating for r in qs}


def get_average_rating(book_id: str) -> float:
    """Calculate the average rating for a specific book."""
    ratings = Rating.objects.filter(book_id=book_id)
    if not ratings.exists():
        return 0.0
    return ratings.aggregate(Avg("rating"))["rating__avg"] or 0.0


def get_number_of_ratings(book_id: str) -> int:
    """Get the number of ratings for a specific book."""
    return Rating.objects.filter(book_id=book_id).count() or 0


def archive_user_evaluations(user, book_id: str):
    """
    Archive all user evaluations
    (ratings and reviews)
    for a specific book
    """
    now = timezone.now()
    Rating.objects.filter(user=user, book_id=book_id, is_archived=False)\
                  .update(is_archived=True, archived_at=now)
    Review.objects.filter(user=user, book_id=book_id, is_archived=False)\
                  .update(is_archived=True, archived_at=now)


def upsert_active_rating(user, book_id: str, value: int):
    """Create or update an active rating for a user and book."""
    row = (Rating.objects
           .filter(user=user, book_id=book_id)
           .order_by("-id")
           .first())
    if row:
        row.is_archived = False
        row.archived_at = None
        row.rating = value
        row.save()
        return row
    return Rating.objects.create(user=user, book_id=book_id, rating=value)


def upsert_active_review(user, book_id: str, content: str):
    """Create or update an active review for a user and book."""
    row = (Review.objects
           .filter(user=user, book_id=book_id)
           .order_by("-id")
           .first())
    if row:
        row.is_archived = False
        row.archived_at = None
        row.content = content
        row.save()
        return row
    return Review.objects.create(user=user, book_id=book_id, content=content)
