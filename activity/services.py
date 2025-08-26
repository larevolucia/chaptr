"""
Service for managing reading statuses and rating.
"""
from django.db.models import Avg
from .models import ReadingStatus, Rating


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
        .filter(user=user, book_id__in=ids)
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
