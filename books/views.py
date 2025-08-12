import os
import requests
import re
from django.shortcuts import render
from django.core.cache import cache
from django.http import Http404

OPERATOR_RE = re.compile(r'\b(intitle|inauthor|inpublisher|subject|isbn|lccn|oclc):', re.I)

# Create your views here.
def home(request):
    return render(request, 'books/home.html')


def book_search(request):
    # read scope and (optional) advanced fields
    field = request.GET.get('field', 'all').strip().lower()
    q_raw = request.GET.get('q', '').strip()

    # Optional advanced fields 
    adv_title = request.GET.get('title', '').strip()
    adv_author = request.GET.get('author', '').strip()
    adv_subject = request.GET.get('subject', '').strip()

    # Build the Google Books 'q' string
    query_for_api = build_q(q_raw, field, adv_title, adv_author, adv_subject)

    books = search_google_books(query_for_api) if query_for_api else []

    # Render the search results
    return render(
        request,
        'books/search_results.html',
        {
            'books': books,
            'query': q_raw,
            'field': field,
            'title': adv_title,
            'author': adv_author,
            'subject': adv_subject,
        }
        )


def build_q(q_raw, field, title, author, subject):
    """
    Build a Google Books 'q' using documented operators
    - If user already typed an operator, pass it through
    - Else apply 'field' to q_raw (intitle/inauthor/subject)
    - Then layer advanced boxes if provided.
    Docs: intitle:, inauthor:, subject: etc. 
    """
    parts = []

    # If the free-text already uses operators, keep it as-is.
    if q_raw:
        if OPERATOR_RE.search(q_raw):
            parts.append(q_raw)
        else:
            if field == 'title':
                parts.append(f'intitle:{q_raw}')
            elif field == 'author':
                parts.append(f'inauthor:{q_raw}')
            elif field == 'subject':
                parts.append(f'subject:{q_raw}')
            else:
                parts.append(q_raw)

    # Advanced boxes additively constrain the search
    if title:
        parts.append(f'intitle:{title}')
    if author:
        parts.append(f'inauthor:{author}')
    if subject:
        parts.append(f'subject:{subject}')

    return " ".join(parts).strip()


def search_google_books(query):
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        return []

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        # "maxResults": 5,
        "printType": "books",
        "orderBy": "relevance",
        "langRestrict": "en"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    data = response.json()

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
    resp = requests.get(url, params={"key": api_key} if api_key else None, timeout=8)
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
