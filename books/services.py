"""
Helper functions for interacting with the Google Books API.
"""
import os
import requests
from django.utils import timezone
from .models import Book

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes/{}"


def fetch_or_refresh_book(volume_id: str, *, force: bool = False, ttl_minutes: int = 1440) -> Book:  # noqa: E501 pylint: disable=line-too-long
    """
    Ensure a Book row exists and is hydrated from Google Books.
    force=True skips TTL checks and fetches now.
    """
    book, _ = Book.objects.get_or_create(pk=volume_id)  # noqa: E501 pylint: disable=no-member

    # Decide whether to fetch
    must_fetch = force or book.needs_refresh(ttl_minutes) or not (book.title or book.authors or book.thumbnail_url)  # noqa: E501 pylint: disable=line-too-long
    if not must_fetch:
        return book

    params = {}
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if api_key:
        params["key"] = api_key

    resp = requests.get(GOOGLE_BOOKS_API_URL.format(volume_id), params=params, timeout=8)  # noqa: E501 pylint: disable=line-too-long
    resp.raise_for_status()
    data = resp.json() or {}
    vi = data.get("volumeInfo", {}) or {}
    links = vi.get("imageLinks", {}) or {}

    # Populate model fields
    book.title = vi.get("title") or ""
    book.authors = vi.get("authors") or None  # JSON list or None
    book.thumbnail_url = links.get("thumbnail") or links.get("smallThumbnail") or ""  # noqa: E501 pylint: disable=line-too-long
    book.language = vi.get("language") or ""
    book.published_date_raw = vi.get("publishedDate") or ""

    # Cache markers (Google also returns a JSON "etag")
    book.etag = data.get("etag") or resp.headers.get("ETag") or ""
    lm = resp.headers.get("Last-Modified")
    if lm:
        try:
            book.last_modified = timezone.now()
        except Exception:
            pass

    book.last_fetched_at = timezone.now()
    book.save()
    return book
