"""
Set the current user's reading status for a Google Books volume.
This view expects a POST request with 'status' in {TO_READ, READING, READ}.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from books.services import fetch_or_refresh_book, safe_redirect_back
from .models import ReadingStatus


# Create your views here
@login_required
@require_POST
def set_reading_status(request, book_id: str):
    """
    Set the current user's reading status for a Google Books volume.
    Expects POST 'status' in {TO_READ, READING, READ}.
    """
    status = (request.POST.get("status") or "").upper()

    if status == "NONE":
        ReadingStatus.objects.filter(user=request.user, book_id=book_id).delete()
        messages.success(request, "Removed your reading status.")
        return safe_redirect_back(request, reverse("book_detail", args=[book_id]))

    valid = {c for c, _ in ReadingStatus.Status.choices}
    if status not in valid:
        messages.error(request, "Invalid status.")
        return safe_redirect_back(request, reverse("book_detail", args=[book_id]))

    # Ensure a Book row exists for FK (uses Google Books API under the hood)
    fetch_or_refresh_book(book_id)  # creates/refreshes books.Book

    # Set the ReadingStatus row
    obj, created = ReadingStatus.objects.get_or_create(
        user=request.user, book_id=book_id, defaults={"status": status}
    )
    if not created:
        obj.status = status
        obj.save(update_fields=["status", "updated_at"])

    messages.success(request, "Saved to your list.")
    return safe_redirect_back(request, reverse("book_detail", args=[book_id]))
