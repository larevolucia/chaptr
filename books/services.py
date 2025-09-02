"""
Helper functions for interacting with the Google Books API.
"""
import logging
import requests
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
from requests.exceptions import RequestException, HTTPError, Timeout
from .models import Book

# --- Config API ----------------------------------------------------
GOOGLE_BOOKS_API_KEY = getattr(settings, "GOOGLE_BOOKS_API_KEY", None)
SEARCH_URL = getattr(settings, "GOOGLE_BOOKS_SEARCH_URL", None)
VOLUME_URL = getattr(settings, "GOOGLE_BOOKS_VOLUME_URL", None)

DEFAULT_TIMEOUT = getattr(settings, "GOOGLE_BOOKS_TIMEOUT", 8)
API_HARD_CAP = 120  # Avoid millions of pages
logger = logging.getLogger(__name__)

if not SEARCH_URL or not VOLUME_URL:
    raise RuntimeError(
        "Missing GOOGLE_BOOKS_SEARCH_URL or"
        " GOOGLE_BOOKS_VOLUME_URL_TMPL in environment."
    )


# --- Helpers -------------------------------------------------------
def safe_redirect_back(request, fallback_url):
    """
    Redirect to the 'next' URL if it's safe,
    otherwise to the fallback URL.
    """
    nxt = request.POST.get("next")
    if nxt and url_has_allowed_host_and_scheme(
        nxt,
        allowed_hosts={request.get_host()}
    ):
        return redirect(nxt)
    return redirect(fallback_url)


def fetch_or_refresh_book(
    volume_id: str, *,
    force: bool = False,
    ttl_minutes: int = 1440
) -> Book:
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

    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    try:
        resp = requests.get(
            VOLUME_URL.format(volume_id),
            params=params,
            timeout=8
            )
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
    book.thumbnail_url = (
        links.get("thumbnail")
        or links.get("smallThumbnail")
        or ""
        )
    book.language = vi.get("language") or ""
    book.published_date_raw = vi.get("publishedDate") or ""

    book.etag = data.get("etag") or resp.headers.get("ETag") or ""

    lm = resp.headers.get("Last-Modified")
    if lm:
        book.last_modified = timezone.now()

    book.last_fetched_at = timezone.now()
    book.save()

    return book


def search_google_books(query, *, start_index=0, max_results=12):
    """Query the Google Books API and return simplified book results.

    This helper performs a GET request to ``/volumes`` with defaults
    (``printType=books``, ``orderBy=relevance``, ``langRestrict=en``).
    Network errors and JSON parsing issues are logged and result in an empty
    list (the UI then renders a "no results" state).

    Args:
        query (str): A valid Google Books query string (``"intitle:django"``).

    Returns:
        list[dict]: A list of lightweight book dicts with keys:
            ``id``, ``title``, ``authors``, ``thumbnail``.
            Returns ``[]`` if the API key is missing or an error occurs.
    """

    if not GOOGLE_BOOKS_API_KEY:
        return [], 0

    params = {
        "q": query,
        "key": GOOGLE_BOOKS_API_KEY,
        "printType": "books",
        "orderBy": "relevance",
        "langRestrict": "en",
        "startIndex": start_index,
        "maxResults": max_results,
    }

    try:
        response = requests.get(
            SEARCH_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()  # Raises HTTPError for bad status codes
        data = response.json() or {}

    except RequestException as e:
        # This catches all requests-related exceptions including HTTPError
        logger.warning("Google Books search failed: %s", e)
        return [], 0
    except ValueError as e:
        # This catches JSON decode errors
        logger.warning("Google Books response parsing failed: %s", e)
        return [], 0

    items = data.get("items") or []
    total_raw = int(data.get("totalItems") or 0)

    books = []

    for item in items:
        volume = item.get("volumeInfo", {})
        books.append({
            "id": item.get("id"),
            "title": volume.get("title"),
            "authors": ', '.join(volume.get("authors", [])),
            "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
        })

    # Avoid millions of pages
    total = min(total_raw, API_HARD_CAP)

    if len(books) < max_results:
        total = start_index + len(books)

    return books, total


def fetch_book_by_id(book_id):
    """Fetch full volume details by Google Books volume ID.

    Performs a GET to ``/volumes/{book_id}`` and normalizes the response into a
    dict for the detail template.
    Failures are logged and surfaced to Django
    by raising ``Http404`` (so the standard 404 page is returned).

    Args:
        book_id (str): Google Books volume identifier.

    Returns:
        dict: Normalized volume data with keys including:
            ``id``, ``title``, ``subtitle``, ``authors``, ``thumbnail``,
            ``publisher``, ``publishedDate``, ``pageCount``, ``categories``,
            ``description``, ``previewLink``, ``infoLink``
    """

    url = VOLUME_URL.format(book_id)
    params = {"key": GOOGLE_BOOKS_API_KEY} if GOOGLE_BOOKS_API_KEY else None

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json() or {}
    except RequestException as e:
        logger.warning(
            "Google Books fetch failed for book_id %s: %s",
            book_id,
            e
            )
        raise Http404("Book not found.") from e
    except ValueError as e:
        logger.warning(
            "Google Books response parsing failed for book_id %s: %s",
            book_id,
            e
            )
        raise Http404("Book not found.") from e

    vi = data.get("volumeInfo", {}) or {}
    return {
        "id": data.get("id"),
        "title": vi.get("title"),
        "subtitle": vi.get("subtitle"),
        "authors": ", ".join(vi.get("authors", [])),
        "thumbnail": (vi.get("imageLinks", {}) or {}).get("thumbnail"),
        "publisher": vi.get("publisher"),
        "publishedDate": vi.get("publishedDate"),
        "pageCount": vi.get("pageCount"),
        "categories": vi.get("categories", []),
        "description": vi.get("description"),
        "previewLink": vi.get("previewLink"),
        "infoLink": vi.get("infoLink"),
    }
