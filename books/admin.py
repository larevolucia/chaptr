"""Admin interface for managing Book objects in Django."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Inspect the cached Book rows (created when a user saves status/rating).
    """
    list_display = (
        "id",
        "title",
        "author_list",
        "language",
        "published_date_raw",
        "has_thumbnail",
        "last_fetched_at",
        "etag_short",
        "last_modified",
        "google_link",
    )
    list_filter = ("language",)
    search_fields = (
        "id",
        "title",
        "authors",
        "published_date_raw",
        "language"
        )
    ordering = ("-last_fetched_at",)
    readonly_fields = (
        "id",
        "title",
        "author_list",
        "language",
        "published_date_raw",
        "thumbnail_preview",
        "etag",
        "last_modified",
        "last_fetched_at",
    )
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "id",
                    "title",
                    "author_list"
                    )
            }
        ),
        (
            "Metadata",
            {
                "fields": (
                    "language",
                    "published_date_raw"
                )
             }
        ),
        (
            "Thumbnail",
            {
                "fields": (
                    "thumbnail_preview",
                    )
            }
        ),
        (
            "HTTP cache",
            {
                "fields": (
                    "etag",
                    "last_modified",
                    "last_fetched_at"
                    )
            }
        ),
    )
    actions = ("refresh_from_google",)

    # ----- presenters -----
    def author_list(self, obj: Book):
        """Return a comma-separated list of authors."""
        return ", ".join(obj.authors or [])
    author_list.short_description = "Authors"

    def has_thumbnail(self, obj: Book):
        """Return a checkmark if the book has a thumbnail."""
        return "✓" if obj.thumbnail_url else "—"
    has_thumbnail.short_description = "Thumb"

    def thumbnail_preview(self, obj: Book):
        """Return a thumbnail image preview."""
        if not obj.thumbnail_url:
            return "—"
        return format_html(
            '<img src="{}" '
            'style="height:120px;border:1px solid #ddd;border-radius:6px;" />',
            obj.thumbnail_url
            )

    def etag_short(self, obj: Book):
        """Return the first 10 characters of the ETag."""
        return (obj.etag or "")[:10]
    etag_short.short_description = "ETag"

    def google_link(self, obj: Book):
        """Return a link to the book on Google Books."""
        return format_html(
            '<a href="https://books.google.com/books?id={}" '
            'target="_blank">Google</a>',
            obj.id
            )
    google_link.short_description = "Link"
