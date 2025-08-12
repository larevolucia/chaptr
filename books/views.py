import os
import requests
from django.shortcuts import render
from django.core.cache import cache
from django.http import Http404

# Create your views here.

def home(request):
    return render(request, 'books/home.html')

def book_search(request):
    query = request.GET.get('q', '').strip()

    books = []
    if query:
        books = search_google_books(query)  # Call the Google Books API search function
    return render(request, 'books/search_results.html', {'books': books, 'query': query})


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
        cache.set(cache_key, book, timeout=60*60)
    return render(
        request,
        "books/book_detail.html",
        {"book": book}
    )
