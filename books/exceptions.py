""" Custom exceptions for book-related operations."""
from django.http import Http404


class BookFetchError(Http404):
    """Raised when fetching book data from Google Books fails."""

    def __init__(
        self,
        message: str,
        volume_id: str | None = None,
        original_exception: Exception | None = None
    ):
        self.volume_id = volume_id
        self.original_exception = original_exception
        super().__init__(self._build_message(message))

    def _build_message(self, message: str) -> str:
        if self.volume_id:
            return f"[Book {self.volume_id}] {message}"
        return message
