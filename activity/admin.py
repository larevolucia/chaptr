""" Admin interface for tracking user reading activity """
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Subquery, OuterRef

from books.models import Book
from .models import ReadingStatus, Rating, Review

# Subquery to show the Book title without a JOIN/extra queries
BOOK_TITLE = Subquery(
    Book.objects.filter(
        pk=OuterRef("book_id")
        ).values("title")[:1]
)


@admin.register(ReadingStatus)
class ReadingStatusAdmin(admin.ModelAdmin):
    """Admin interface for tracking user reading activity."""
    list_display = (
        "user", "book_id", "book_title", "status", "updated_at", "google_link"
    )
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "book_id")
    date_hierarchy = "updated_at"
    ordering = ("-updated_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_title=BOOK_TITLE)

    def book_title(self, obj):
        """Return the title of the book."""
        return getattr(obj, "_book_title", None) or "—"

    book_title.admin_order_field = "_book_title"
    book_title.short_description = "Title"

    def google_link(self, obj):
        """Return a link to the book on Google Books."""
        return format_html(
            '<a href="https://books.google.com/books?id={}" target="_blank">Google</a>',  # noqa: E501 pylint: disable=line-too-long
            obj.book_id,
        )
    google_link.short_description = "Link"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin interface for tracking user reading activity."""
    list_display = (
        "user", "book_id", "book_title", "rating", "updated_at", "google_link"
        )
    list_filter = ("rating",)
    search_fields = ("user__username", "user__email", "book_id")
    date_hierarchy = "updated_at"
    ordering = ("-updated_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_title=BOOK_TITLE)

    def book_title(self, obj):
        """Return the title of the book."""
        return getattr(obj, "_book_title", None) or "—"

    book_title.admin_order_field = "_book_title"
    book_title.short_description = "Title"

    def google_link(self, obj):
        """Return a link to the book on Google Books."""
        return format_html(
            '<a href="https://books.google.com/books?id={}" target="_blank">Google</a>',  # noqa: E501 pylint: disable=line-too-long
            obj.book_id,
        )
    google_link.short_description = "Link"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for managing book reviews."""
    list_display = (
        "user", "book_id", "book_title", "content", "created_at", "updated_at"
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "book_id", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_title=BOOK_TITLE)

    def book_title(self, obj):
        """Return the title of the book."""
        return getattr(obj, "_book_title", None) or "—"

    book_title.admin_order_field = "_book_title"
    book_title.short_description = "Title"
