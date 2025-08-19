"""
Helper functions for managing book data.
"""
from email.utils import parsedate_to_datetime
from typing import Optional
import requests
from django.utils import timezone
from .models import Book

BOOKS_API_BASE = "https://www.googleapis.com/books/v1/volumes/"


def fetch_or_refresh_book(volume_id, force=False, session: Optional[requests.Session] = None) -> Book:  # noqa: E501 pylint: disable=line-too-long
    """
    Ensure a Book row exists and is fresh(ish).
    - Creates the row if missing.
    - Sends conditional headers (ETag / If-Modified-Since) when possible.
    - Saves only when Google returns updated data.
    """
    # Check database for existing book
    # Creates one if missing
    book, _ = Book.objects.get_or_create(pk=volume_id)

    # If book is fresh, return it
    if not force and not book.needs_refresh():
        return book

    # Prepare headers for conditional GET
    headers = {}
    if book.etag:
        headers["If-None-Match"] = book.etag
    if book.last_modified:
        headers["If-Modified-Since"] = book.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")  # noqa: E501 pylint: disable=line-too-long

    # If book is not fresh, fetch from Google Books API
    # https://requests.readthedocs.io/en/latest/user/advanced/#conditional-requests
    s = session or requests.Session()
    r = s.get(f"{BOOKS_API_BASE}{volume_id}", headers=headers, timeout=10)

    # Handle 304 response: not modified
    if r.status_code == 304:
        book.last_fetched_at = timezone.now()
        book.save(update_fields=["last_fetched_at"])
        return book

    # handle other responses
    r.raise_for_status()
    book_data = r.json()
    vi = book_data.get("volumeInfo", {}) or {}
    images = vi.get("imageLinks", {}) or {}

    # Map minimal fields
    book.title = vi.get("title") or ""
    book.authors = vi.get("authors") or None
    book.thumbnail_url = images.get("thumbnail") or images.get("smallThumbnail") or ""  # noqa: E501
    book.language = vi.get("language") or ""
    book.published_date_raw = vi.get("publishedDate") or ""

    # Try to read the ETag header from the HTTP response
    etag = r.headers.get("ETag") or book_data.get("etag") or ""
    book.etag = etag.strip('"')
    # Try to read the Last-Modified HTTP header, if present
    lm = r.headers.get("Last-Modified")
    # Convert from string
    book.last_modified = parsedate_to_datetime(lm) if lm else None
    # Record NextChaptr last fetched timestamp
    book.last_fetched_at = timezone.now()

    book.save()
    return book
