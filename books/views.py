"""
Views for NextChaptr's Google Books search and detail pages.

This module exposes:
- Simple home view.
- Search flow that builds a Google Books query (with basic operators)
  and renders results.
- Detail flow that fetches a single volume by ID with low-level caching.
"""
import os
import re
import logging
import requests
from requests import RequestException
from django.core.paginator import Paginator
from django.shortcuts import render,  redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import Http404
from django.db.utils import ProgrammingError, OperationalError
from activity.models import Rating, ReadingStatus, Review
from activity.forms import ReviewForm
from activity.services import (
    statuses_map_for,
    ratings_map_for,
    get_average_rating,
    get_number_of_ratings
)

# Create your views here.
logger = logging.getLogger(__name__)
OPERATOR_RE = re.compile(r'\b(intitle|inauthor|inpublisher|subject|isbn|lccn|oclc):', re.I)  # noqa: E501  pylint: disable=line-too-long


def _genres():
    return [
        ("Sci-Fi", "science fiction"),
        ("Mystery", "mystery"),
        ("Non-Fiction", "nonfiction"),
        ("Fantasy", "fantasy"),
        ("Horror", "horror"),
        ("Romance", "romance"),
        ("Thriller", "thriller"),
        ("Biography", "biography"),
        ("Self-Help", "self-help"),
        ("Children", "children"),
        ("Cookbooks", "cookbooks"),
        ("Graphic Novels", "graphic novels"),
        ("Poetry", "poetry"),
        ("Classics", "classics"),
        ("Comics", "comics"),
        ("Business", "business"),
        ("Science", "science"),
        ("History", "history"),
        ("Travel", "travel"),
        ("Sports", "sports"),
        ("Memoir", "memoir"),
        ("Religion", "religion"),
        ("Spirituality", "spirituality"),
        ("Technology", "technology"),
    ]


def home(request):
    """
    Render the landing page for the books app.
    """
    genres = _genres()
    return render(request, "books/home.html", {"genres": genres})


def build_q(q_raw, field, _title_unused="", _author_unused="", _subject_unused=""):  # noqa: E501 pylint: disable=line-too-long
    """
    Build a Google Books 'q' using a single dropdown field.
    - If user already typed an operator,
    pass it through unchanged.
    - Else apply the dropdown operator
    (intitle/inauthor/subject)
    or leave as-is for 'all'.
    * Unused parameters are ignored.
    """
    q_raw = (q_raw or "").strip()
    field = (field or "all").strip().lower()

    if not q_raw:
        return ""

    # pass-through if user already used an operator
    if OPERATOR_RE.search(q_raw):
        return q_raw

    # apply operator based on dropdown
    if field == "title":
        return f"intitle:{q_raw}"
    if field == "author":
        return f"inauthor:{q_raw}"
    if field == "subject":
        return f"subject:{q_raw}"
    return q_raw  # field == "all"


def book_search(request):
    """Handle the search page:
       build query, call API helper, render results.

    Reads ``field`` and ``q`` from ``request.GET``,
    normalizes them via `build_q`,
    calls `search_google_books` if non-empty,
    and renders ``books/search_results.html``.

    Args:
        request: The current request

    Returns:
        Response: Rendered search results template with context:
            - ``books`` (list[dict]): Minimal book metadata for display.
            - ``query`` (str): The original search text.
            - ``field`` (str): The selected scope (all/title/author/subject).
    """
    # read scope and basic query only
    field = request.GET.get('field', 'all').strip().lower()
    q_raw = request.GET.get('q', '').strip()

    if not q_raw:
        if request.GET:
            messages.info(request, "Type something to search.")
        return render(request, "books/home.html", {"genres": _genres()})

    query_for_api = build_q(q_raw, field)

    per_page = 12
    try:
        current_page = int(request.GET.get("page") or 1)
    except ValueError:
        current_page = 1
    start_index = (current_page - 1) * per_page

    books, total = search_google_books(
        query_for_api,
        start_index=start_index,
        max_results=per_page
        )

    ids = [r["id"] for r in books]
    user = getattr(request, "user", AnonymousUser())
    status_map = statuses_map_for(user, ids)
    rating_map = ratings_map_for(user, ids)

    labels = dict(ReadingStatus.Status.choices)

    for b in books:
        status = (status_map.get(b["id"]) or {}).get("status")
        b["user_status"] = status
        b["user_status_label"] = labels.get(status)
        b["user_rating"] = rating_map.get(b["id"], 0)
        b["avg_rating"] = get_average_rating(b["id"])
        b["num_ratings"] = get_number_of_ratings(b["id"])

    paginator = Paginator(range(total), per_page)
    page_obj = paginator.get_page(current_page)
    page_obj.object_list = books
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=1,
        on_ends=1
        )

    # Render the search results
    return render(
        request,
        'books/search_results.html',
        {
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'page_range': list(page_range),
            'query': q_raw,
            'field': field,
        }
    )


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
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        return [], 0

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        "printType": "books",
        "orderBy": "relevance",
        "langRestrict": "en",
        "startIndex": start_index,
        "maxResults": max_results,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
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
    API_HARD_CAP = 120
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

    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    params = {"key": api_key} if api_key else None

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json() or {}
    except RequestException as e:
        logger.warning("Google Books fetch failed for book_id %s: %s", book_id, e)  # noqa: E501
        raise Http404("Book not found.") from e
    except ValueError as e:
        logger.warning("Google Books response parsing failed for book_id %s: %s", book_id, e)  # noqa: E501 pylint: disable=line-too-long
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


def book_detail(request, book_id):
    """Render the detail page for a single book with 1-hour caching.

    Checks a low-level cache for the normalized volume dict.
    If missing, calls :func:`fetch_book_by_id`,
    stores the result under the key ``"gbooks:vol:{book_id}"``
    and renders ``books/book_detail.html``.

    Args:
        request: The current request.
        book_id (str): Google Books volume identifier.

    Returns:
        response: The rendered detail template with
        context ``{"book": <dict>}``.
    """

    cache_key = f"gbooks:vol:{book_id}"
    book = cache.get(cache_key)
    if not book:
        book = fetch_book_by_id(book_id)
        cache.set(cache_key, book, timeout=60*60)

    book["user_status"] = None
    book["user_status_label"] = None
    book["user_rating"] = 0

    form = None
    reviews = []
    my_review = None
    edit_mode = False

    user = getattr(request, "user", AnonymousUser())
    if getattr(user, "is_authenticated", False):
        # use `user` below instead of `request.user`
        rs = (
            ReadingStatus.objects
            .filter(user=user, book_id=book_id)
            .only("status")
            .first()
              )
        try:
            # reading status
            rs = (
                ReadingStatus.objects
                .filter(user=request.user, book_id=book_id)
                .only("status")
                .first()
            )
            status = rs.status if rs else None
            labels = dict(ReadingStatus.Status.choices)
            book["user_status"] = status
            book["user_status_label"] = labels.get(status)
            # rating
            r = (
                Rating.objects
                .filter(user=request.user, book_id=book_id)
                .only("rating")
                .first()
            )
            book["user_rating"] = r.rating if r else 0
            # avg rating
            book["avg_rating"] = get_average_rating(book_id)
            book["num_ratings"] = get_number_of_ratings(book_id)
            # book reviews
            reviews = (
                Review.objects
                .select_related("user")
                .filter(book_id=book_id)
                .order_by("-created_at")
            )
            # check if user has already written a review
            # user’s review (if any)
            my_review = (
                Review.objects
                .filter(user=request.user, book_id=book_id)
                .first()
            )

            # only build a blank form if the user has not reviewed yet
            form = (
                None if my_review
                else ReviewForm(user=request.user, book_id=book_id)
            )

            if my_review:
                reviews = reviews.exclude(pk=my_review.pk)

            # Determine if we are in edit mode
            edit_mode = request.GET.get("edit") == "1" and my_review is not None

            if edit_mode:
                # show a prefilled form to edit
                form = ReviewForm(user=request.user, book_id=book_id, instance=my_review)
                # optionally hide the “your review” from the list while editing
                reviews = reviews.exclude(pk=my_review.pk)
            else:
                # show a blank form only if the user hasn't reviewed yet
                form = None if my_review else ReviewForm(user=request.user, book_id=book_id)

        except (ProgrammingError, OperationalError):
            # db not ready
            pass

    return render(
        request,
        "books/book_detail.html",
        {
            "book": book,
            "form": form,
            "reviews": reviews,
            "my_review": my_review,
            "edit_mode": edit_mode,
        }
    )
