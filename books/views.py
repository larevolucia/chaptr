# from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import os

def test_api_key(request):
    key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    return JsonResponse({"api_key_loaded": bool(key), "value": key})
