"""
Views for NextChaptr's Google Books search and detail pages.

This module exposes:
- Simple home view.
- Search flow that builds a Google Books query (with basic operators)
  and renders results.
- Detail flow that fetches a single volume by ID with low-level caching.
"""
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.utils import ProgrammingError, OperationalError
from activity.models import Rating, ReadingStatus, Review
from activity.forms import ReviewForm
from activity.services import (
    statuses_map_for,
    ratings_map_for,
    get_average_rating,
    get_number_of_ratings
)
from books.services import (
    search_google_books,
    fetch_book_by_id
)
from books.utils import _genres, build_q
# Create your views here.


def home(request):
    """
    Render the landing page for the books app.
    """
    genres = _genres()
    return render(request, "books/home.html", {"genres": genres})


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
        try:
            # reading status
            rs = (
                ReadingStatus.objects
                .filter(user=user, book_id=book_id)
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
                .filter(user=user, book_id=book_id, is_archived=False)
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
                .filter(book_id=book_id, is_archived=False)
                .order_by("-created_at")
            )
            # check if user has already written a review
            # user’s review (if any)
            my_review = (
                Review.objects
                .filter(user=user, book_id=book_id, is_archived=False)
                .first()
            )

            # only build a blank form if the user has not reviewed yet
            form = (
                None if my_review
                else ReviewForm(user=user, book_id=book_id)
            )

            if my_review:
                reviews = reviews.exclude(pk=my_review.pk)

            # Determine if we are in edit mode
            edit_mode = (
                request.GET.get("edit") == "1"
                and my_review is not None
                )

            if edit_mode:
                # show a prefilled form to edit
                form = ReviewForm(
                    user=user,
                    book_id=book_id,
                    instance=my_review
                    )
                # optionally hide the “your review” from the list while editing
                reviews = reviews.exclude(pk=my_review.pk)
            else:
                # show a blank form only if the user hasn't reviewed yet
                form = None if my_review else ReviewForm(
                    user=user,
                    book_id=book_id
                    )

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
