import os
import re
import requests
from requests import RequestException
from django.shortcuts import render
from django.core.cache import cache
from django.http import Http404


# Create your views here.

OPERATOR_RE = re.compile(r'\b(intitle|inauthor|inpublisher|subject|isbn|lccn|oclc):', re.I)  # noqa: E501  pylint: disable=line-too-long


def home(request):
    return render(request, 'books/home.html')


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
    # read scope and basic query only
    field = request.GET.get('field', 'all').strip().lower()
    q_raw = request.GET.get('q', '').strip()

    query_for_api = build_q(q_raw, field)
    books = search_google_books(query_for_api) if query_for_api else []

    # Render the search results
    return render(
        request,
        'books/search_results.html',
        {
            'books': books,
            'query': q_raw,
            'field': field,
        }
    )


def search_google_books(query):
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        return []

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        "printType": "books",
        "orderBy": "relevance",
        "langRestrict": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        data = response.json()
    except RequestException as exc:
        # This catches all requests-related exceptions including HTTPError
        raise ValueError(f"Google Books search failed: {exc}") from exc
    except ValueError as exc:
        # This catches JSON decode errors
        raise ValueError(f"Google Books response parsing failed: {exc}") from exc  # noqa: E501
    books = []
    for item in data.get("items", []):
        volume = item.get("volumeInfo", {})
        books.append({
            "id": item.get("id"),
            "title": volume.get("title"),
            "authors": ', '.join(volume.get("authors", [])),
            "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
        })

    return books


def fetch_book_by_id(book_id):
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    resp = requests.get(url, params={"key": api_key} if api_key else None, timeout=8)  # noqa: E501
    if resp.status_code != 200:
        raise Http404("Book not found.")
    data = resp.json() or {}
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
    cache_key = f"gbooks:vol:{book_id}"
    book = cache.get(cache_key)
    if not book:
        book = fetch_book_by_id(book_id)
        # set cache for 1 hour
        cache.set(cache_key, book, timeout=60*60)
    return render(
        request,
        "books/book_detail.html",
        {"book": book}
    )
