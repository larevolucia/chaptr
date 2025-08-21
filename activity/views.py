"""
Set the current user's reading status for a Google Books volume.
This view expects a POST request with 'status' in {TO_READ, READING, READ}.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse

from books.services import fetch_or_refresh_book, safe_redirect_back
from books.models import Book
from .models import ReadingStatus, Rating
from .forms import ReviewForm

# Create your views here
@login_required
@require_POST
def add_reading_status(request, book_id: str):
    """
    Set the current user's reading status for a Google Books volume.
    Expects POST 'status' in {TO_READ, READING, READ}.
    """
    status = (request.POST.get("status") or "").upper()

    if status == "NONE":
        ReadingStatus.objects.filter(
            user=request.user, book_id=book_id
        ).delete()
        messages.success(request, "Removed your reading status.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )

    valid = {c for c, _ in ReadingStatus.Status.choices}
    if status not in valid:
        messages.error(request, "Invalid status.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )
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
    return safe_redirect_back(
        request, reverse("book_detail", args=[book_id])
    )


@login_required
@require_POST
def add_rating(request, book_id: str):
    """Set the current user's rating for specific book."""
    rating = request.POST.get("rating")

    if rating is None:
        messages.error(request, "Invalid rating.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )

    try:
        rating = int(rating)
    except ValueError:
        messages.error(request, "Invalid rating.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )

    # Handle rating removal (when rating is 0)
    if rating == 0:
        Rating.objects.filter(user=request.user, book_id=book_id).delete()
        messages.info(request, "Removed your rating.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )

    # Validate rating range
    if rating < 1 or rating > 5:
        messages.error(request, "Rating must be between 1 and 5.")
        return safe_redirect_back(
            request, reverse("book_detail", args=[book_id])
        )

    # Ensure a Book row exists for FK
    fetch_or_refresh_book(book_id)

    # Create or update the rating
    rating_obj, created = Rating.objects.get_or_create(
        user=request.user,
        book_id=book_id,
        defaults={"rating": rating}
    )

    if not created:
        rating_obj.rating = rating
        rating_obj.save(update_fields=["rating", "updated_at"])
        messages.success(request, "Updated your rating.")
    else:
        messages.success(request, "Saved your rating.")

    return safe_redirect_back(request, reverse("book_detail", args=[book_id]))


@login_required
def add_review(request, book_id):
    """Add a review for a book."""
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, user=request.user, book=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been posted.")
            return redirect("book_detail", book_id=book_id)
    else:
        form = ReviewForm(user=request.user, book=book)

    return render(
        request,
        "activity/review_form.html",
        {"form": form, "book": book}
    )
