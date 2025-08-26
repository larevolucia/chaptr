from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from books.models import Book
from activity.models import ReadingStatus

# Create your views here.

@login_required
def library(request):
    # These three queries are easy to read and reason about:
    to_read = (
        Book.objects
        .filter(reading_statuses__user=request.user,
                reading_statuses__status=ReadingStatus.Status.TO_READ)
        .only("id", "title", "thumbnail_url")         # load just what you need
        .distinct()
    )
    reading = (
        Book.objects
        .filter(reading_statuses__user=request.user,
                reading_statuses__status=ReadingStatus.Status.READING)
        .only("id", "title", "thumbnail_url")
        .distinct()
    )
    read = (
        Book.objects
        .filter(reading_statuses__user=request.user,
                reading_statuses__status=ReadingStatus.Status.READ)
        .only("id", "title", "thumbnail_url")
        .distinct()
    )

    return render(
        request,
        "library/library.html",
        {"to_read": to_read, "reading": reading, "read": read}
        )
