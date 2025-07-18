# from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import os
import requests


def book_search(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)
    
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        return JsonResponse({"error": "API key not set"}, status=500)

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": api_key,
        "maxResults": 5,
        "langRestrict": "en"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch data from Google Books API"}, status=response.status_code)

    data = response.json()

    # Extract relevant book information
    # books = []

    # for item in data.get("items", []):
    #     volume_info = item.get("volumeInfo", {})
    #     books.append({
    #         "title": volume_info.get("title"),
    #         "authors": volume_info.get("authors"),
    #         "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail"),
    #     })

    filtered_items = [
        item for item in data.get("items", [])
        if item.get("volumeInfo", {}).get("language") == "en"
    ]

    return JsonResponse({"results": filtered_items})



def test_api_key(request):
    key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    return JsonResponse({"api_key_loaded": bool(key), "value": key})
