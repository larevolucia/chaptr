"""
Service for managing reading statuses.
"""
from .models import ReadingStatus


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
