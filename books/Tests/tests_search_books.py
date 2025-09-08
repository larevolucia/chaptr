"""Tests for the search books views and helpers.

Covers:
- Query building via `build_q`.
- Search view wiring to `search_google_books`.
- Google Books list search happy/empty paths.
- Single volume fetch mapping and 404 behavior.

Notes:
- External HTTP calls are patched.
- Cache is cleared where needed to avoid cross-test state.
"""
import os
from unittest.mock import patch, Mock
from requests import HTTPError
from django.core.cache import cache
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from books.services import (
    search_google_books,
    fetch_book_by_id,
)
from books.views import book_search
from books.utils import build_q

User = get_user_model()

REALISTIC_DETAIL_JSON = {
    "id": "AkVWPbrWKGEC",
    "volumeInfo": {
        "title": "Wuthering heights",
        "subtitle": "A Nice Subtitle",
        "authors": ["Emily Bronte"],
        "publisher": "Rowman & Littlefield",
        "publishedDate": "1992-01-01",
        "pageCount": 206,
        "categories": ["Poetry"],
        "description": "Some description.",
        "previewLink": "http://example.test/preview",
        "infoLink": "http://example.test/info",
        "imageLinks": {"thumbnail": "http://thumb/poems.jpg"},
    },
}


class BuildQTests(TestCase):
    """Unit tests for `build_q` query construction."""
    def test_build_q_with_field_author(self):
        """Applies `inauthor:` when field is 'author'."""
        q = build_q("emily bronte", "author")
        self.assertEqual(q, "inauthor:emily bronte")

    def test_build_q_preserves_existing_operator_even_if_field_differs(self):
        """Passes through when user already supplied an operator."""
        q = build_q("intitle:wuthering heights", "author")
        self.assertEqual(q, "intitle:wuthering heights")

    def test_build_q_all_keeps_plain_text(self):
        """Leaves query unchanged when field is 'all'."""
        q = build_q("wuthering heights", "all")
        self.assertEqual(q, "wuthering heights")

    def test_build_q_subject_applies_operator(self):
        """Applies `subject:` when field is 'subject'."""
        q = build_q("poetry", "subject")
        self.assertEqual(q, "subject:poetry")

    def test_build_q_empty_returns_empty(self):
        """Returns empty string for empty input."""
        q = build_q("", "author")
        self.assertEqual(q, "")


class BookSearchViewTests(TestCase):
    """Integration test for the search view wiring to the helper."""
    def setUp(self):
        """Initialize a RequestFactory for view calls."""
        self.rf = RequestFactory()

    @patch("books.views.search_google_books")
    def test_book_search_uses_built_query(self, mock_search):
        """Test that the search view uses the built query."""
        mock_search.return_value = ([], 0)
        req = self.rf.get("/books/search", {"field": "author", "q": "emily bronte"})  # noqa: E501
        resp = book_search(req)
        self.assertEqual(resp.status_code, 200)
        # ensure build_q result was used
        called_args = mock_search.call_args.args[0]
        self.assertEqual(called_args, "inauthor:emily bronte")

    def test_book_search_no_query_renders(self):
        """Test that the search view renders with no query."""
        req = self.rf.get(
            "/books/search",
            {"field": "subject", "q": "jellyfish age backwards"}
            )
        resp = book_search(req)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="no-results"')


class SearchGoogleBooksTests(TestCase):
    """Integration tests for the Google Books API search functionality."""
    @patch.dict(os.environ, {"GOOGLE_BOOKS_API_KEY": "fake-key"}, clear=False)
    @patch("books.services.requests.get")
    def test_returns_parsed_list_on_200(self, mock_get):
        """Test that a successful API call returns a parsed list."""
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {
            "totalItems": 100,
            "items": [
                {
                    "id": "X",
                    "volumeInfo": {
                        "title": "T",
                        "authors": ["A"],
                        "imageLinks": {"thumbnail": "http://t"}
                    }
                },
                {
                    "id": "Y",
                    "volumeInfo": {
                              "title": "U",
                              "authors": ["B"],
                              "imageLinks": {"thumbnail": "http://u"}
                          }
                }
                      ]
        }
        mock_get.return_value = mock_resp

        books, _total = search_google_books("inauthor:emily bronte")
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0]["id"], "X")
        self.assertEqual(books[0]["authors"], "A")
        self.assertEqual(books[0]["title"], "T")
        self.assertEqual(books[0]["thumbnail"], "https://t")
        self.assertEqual(books[1]["id"], "Y")
        self.assertEqual(books[1]["authors"], "B")
        self.assertEqual(books[1]["title"], "U")
        self.assertEqual(books[1]["thumbnail"], "https://u")

    @patch.dict(os.environ, {"GOOGLE_BOOKS_API_KEY": "fake-key"}, clear=False)
    @patch("books.services.requests.get")
    def test_non_200_or_exception_returns_empty(self, mock_get):
        """Test that non-200 responses or exceptions return an empty list."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = HTTPError("500")
        mock_get.return_value = mock_resp
        books, _total = search_google_books("X")
        self.assertEqual(books, [])


class FetchBookByIdTests(TestCase):
    """Integration tests for the fetch_book_by_id function."""
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()

    @patch("books.services.requests.get")
    def test_fetch_book_by_id_success_maps_fields(self, mock_get):
        """Test that fetch_book_by_id maps fields correctly."""
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = REALISTIC_DETAIL_JSON
        mock_get.return_value = mock_resp

        data = fetch_book_by_id("AkVWPbrWKGEC")
        self.assertEqual(data["id"], "AkVWPbrWKGEC")
        self.assertEqual(data["title"], "Wuthering heights")
        self.assertEqual(data["subtitle"], "A Nice Subtitle")
        self.assertEqual(data["authors"], "Emily Bronte")
        self.assertEqual(data["publisher"], "Rowman & Littlefield")
        self.assertEqual(data["publishedDate"], "1992-01-01")
        self.assertEqual(data["pageCount"], 206)
        self.assertIn("Poetry", data["categories"])
        self.assertEqual(data["description"], "Some description.")
        self.assertTrue(data["thumbnail"].startswith("http"))
        self.assertEqual(data["previewLink"], "http://example.test/preview")

    @patch("books.services.requests.get")
    def test_fetch_book_by_id_404_on_non_200(self, mock_get):
        """Test that fetch_book_by_id raises Http404 on non-200."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = HTTPError("404")
        mock_get.return_value = mock_resp
        with self.assertRaises(Http404):
            fetch_book_by_id("nonexistent")
