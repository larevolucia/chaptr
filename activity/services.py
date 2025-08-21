"""
Service for managing reading statuses and rating.
"""
from .models import ReadingStatus, Rating


def statuses_map_for(user, book_ids):
    """
    Returns {book_id: {"status": "..."}}
    """
    if not user.is_authenticated or not book_ids:
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
