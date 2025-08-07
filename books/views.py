from django.shortcuts import render
from django.http import JsonResponse
import os
import requests


# Create your views here.

def home(request):
    return render(request, 'books/home.html')

def book_search(request):
    query = request.GET.get('q')
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
        "maxResults": 5,
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
            "title": volume.get("title"),
            "authors": ', '.join(volume.get("authors", [])),
            "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
        })

    return books
