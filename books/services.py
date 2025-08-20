"""
Helper functions for interacting with the Google Books API.
"""
import os
import requests
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from requests.exceptions import RequestException, HTTPError, Timeout
from .models import Book

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes/{}"


def safe_redirect_back(request, fallback_url):
    """Redirect to the 'next' URL if it's safe, otherwise to the fallback URL."""
    nxt = request.POST.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(fallback_url)


def fetch_or_refresh_book(volume_id: str, *, force: bool = False, ttl_minutes: int = 1440) -> Book:  # noqa: E501 pylint: disable=line-too-long
    """
    Ensure a Book row exists and is hydrated from Google Books.
    force=True skips TTL checks and fetches now.
    """
    book, _ = Book.objects.get_or_create(pk=volume_id)

    must_fetch = (
        force or
        book.needs_refresh(ttl_minutes) or
        not (book.title or book.authors or book.thumbnail_url)
    )
    if not must_fetch:
        return book

    params = {}
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(GOOGLE_BOOKS_API_URL.format(volume_id), params=params, timeout=8)  # noqa: E501 pylint: disable=line-too-long
        resp.raise_for_status()
    except (HTTPError, Timeout) as e:
        raise RuntimeError(f"Failed to fetch book data: {e}") from e
    except RequestException as e:
        raise RuntimeError(f"Request error while fetching book: {e}") from e

    data = resp.json() or {}
    vi = data.get("volumeInfo", {}) or {}
    links = vi.get("imageLinks", {}) or {}

    # Populate model fields
    book.title = vi.get("title") or ""
    book.authors = vi.get("authors") or None
    book.thumbnail_url = links.get("thumbnail") or links.get("smallThumbnail") or ""  # noqa: E501
    book.language = vi.get("language") or ""
    book.published_date_raw = vi.get("publishedDate") or ""

    book.etag = data.get("etag") or resp.headers.get("ETag") or ""

    lm = resp.headers.get("Last-Modified")
    if lm:
        book.last_modified = timezone.now()

    book.last_fetched_at = timezone.now()
    book.save()

    return book
