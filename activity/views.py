"""
Set the current user's reading status for a Google Books volume.
This view expects a POST request with 'status' in {TO_READ, READING, READ}.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse

from books.services import fetch_or_refresh_book, safe_redirect_back
from .services import (
    archive_user_evaluations,
    upsert_active_rating,
    upsert_active_review
    )
from .models import ReadingStatus, Rating, Review
from .forms import ReviewForm


# Create your views here
@login_required
@require_POST
def set_reading_status(request, book_id: str):
    """
    Set the current user's reading status for a Google Books volume.
    Expects POST 'status' in {TO_READ, READING, READ}.
    """
    status = (
        request.POST.get("status")
        or
        request.GET.get("status")
        or
        ""
        ).upper()

    if status == "NONE":
        ReadingStatus.objects.filter(
            user=request.user, book_id=book_id
        ).delete()
        archive_user_evaluations(request.user, book_id)
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
    ReadingStatus.objects.get_or_create(
        user=request.user,
        book_id=book_id,
        defaults={"status": ReadingStatus.Status.READ},
    )

    # Unarchive/reuse last row or create fresh active
    upsert_active_rating(request.user, book_id, rating)
    messages.success(request, "Saved your rating.")

    return safe_redirect_back(request, reverse("book_detail", args=[book_id]))


@login_required
def add_review(request, book_id):
    """Add a review for a book.

    Args:
        request (HttpRequest): The HTTP request object.
        book_id (str): The ID of the book being reviewed.

    Returns:
        HttpResponse: The response object.
    """
    fetch_or_refresh_book(book_id)
    existing = Review.objects.filter(
        user=request.user,
        book_id=book_id,
        is_archived=False
        ).first()

    if request.method == "POST":
        form = ReviewForm(
            request.POST,
            user=request.user,
            book_id=book_id,
            instance=existing
            )
        if form.is_valid():
            # Ensure a status exists if posting a review
            ReadingStatus.objects.get_or_create(
                user=request.user,
                book_id=book_id,
                defaults={"status": ReadingStatus.Status.READ}
            )
            content = (request.POST.get("content") or "").strip()
            if content:
                upsert_active_review(request.user, book_id, content)
                messages.success(
                    request,
                    "Updated your review."
                    if existing
                    else "Your review has been posted."
                    )
            return redirect("book_detail", book_id=book_id)
    else:
        instance = existing if request.GET.get("edit") and existing else None
        form = ReviewForm(
            user=request.user,
            book_id=book_id,
            instance=instance
            )

    return redirect(
        "book_detail", book_id=book_id
    )


@login_required
@require_POST
def delete_review(request, book_id: str, review_id: int):
    """
    Delete a specific review for a book.
    Only the review owner can delete.
    """
    review = get_object_or_404(Review, pk=review_id, book_id=book_id)

    # Authorization guard: only owner can delete
    if review.user_id != request.user.id:
        return HttpResponseForbidden("You can only delete your own review.")

    review.delete()
    messages.success(request, "Your review was deleted.")
    return redirect("book_detail", book_id=book_id)
