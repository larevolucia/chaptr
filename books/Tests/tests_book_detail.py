""" Tests for the book detail view."""
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.urls import reverse
from django.contrib.auth import get_user_model
from books.views import (
    book_detail
)

User = get_user_model()


class BookDetailViewTests(TestCase):
    """Integration tests for the book detail view."""
    def setUp(self):
        """Initialize a RequestFactory for view calls and clears cache."""
        self.rf = RequestFactory()
        cache.clear()

        self.sample_book_data = {
            "id": "test_book_id_123",
            "title": "Test Book Title",
            "subtitle": "A Test Subtitle",
            "authors": "Test Author, Another Author",
            "thumbnail": "https://example.com/thumbnail.jpg",
            "publisher": "Test Publisher",
            "publishedDate": "2023-01-01",
            "pageCount": 250,
            "categories": ["Fiction", "Adventure"],
            "description": "This is a test book description.",
            "previewLink": "https://example.com/preview",
            "infoLink": "https://example.com/info",
        }

    @patch("books.views.fetch_book_by_id")
    def test_book_detail_renders_200_and_context(self, mock_fetch):
        """Test that the book detail view renders correctly."""
        mock_fetch.return_value = {
            "id": "AkVWPbrWKGEC",
            "title": "Wuthering heights",
            "authors": "Emily Bronte",
            "thumbnail": "http://thumb",
            "publisher": "Rowman & Littlefield",
            "publishedDate": "1992-01-01",
            "pageCount": 206,
            "categories": ["Poetry"],
            "description": "Some description.",
            "previewLink": "http://example.test/preview",
            "infoLink": "http://example.test/info",
            "subtitle": "A Nice Subtitle",
        }
        req = self.rf.get("/books/AkVWPbrWKGEC")
        resp = book_detail(req, "AkVWPbrWKGEC")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Wuthering heights", resp.content)
        self.assertIn(b"Emily Bronte", resp.content)
        self.assertIn(b"/cover/AkVWPbrWKGEC", resp.content)
        self.assertIn(b"1992-01-01", resp.content)
        self.assertIn(b"206", resp.content)
        self.assertIn(b"Poetry", resp.content)
        self.assertIn(b"Some description.", resp.content)
        self.assertIn(b"A Nice Subtitle", resp.content)
        self.assertIn(b"Rowman &amp; Littlefield", resp.content)

    @patch("books.views.fetch_book_by_id")
    def test_book_detail_caches_volume(self, mock_fetch):
        """Test that the book detail view caches the fetched volume."""
        # First hit -> calls fetch and caches
        mock_fetch.return_value = {"id": "ID1", "title": "T"}
        req1 = self.rf.get("/books/ID1")
        resp1 = book_detail(req1, "ID1")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(mock_fetch.call_count, 1)

        # Second hit -> should be served from cache (no extra fetch)
        req2 = self.rf.get("/books/ID1")
        resp2 = book_detail(req2, "ID1")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(mock_fetch.call_count, 1)  # unchanged => cached

    @patch('books.views.fetch_book_by_id')
    def test_book_detail_search_form_inclusion(self, mock_fetch):
        """Test that the book detail page includes the search form."""
        # Mock the API call
        mock_fetch.return_value = self.sample_book_data

        url = reverse("book_detail", kwargs={"book_id": "test_book_id_123"})
        resp = self.client.get(url)

        # Check for search form elements based on search_form.html
        self.assertContains(resp, 'name="q"', html=False)
        self.assertContains(resp, 'name="field"', html=False)
        self.assertContains(resp, 'role="search"', html=False)
        self.assertContains(resp, 'aria-label="Site search"', html=False)

        # Check for specific form action
        book_search_url = reverse("book_search")
        self.assertContains(resp, f'action="{book_search_url}"', html=False)

        # Check for search form structure
        self.assertContains(
            resp,
            'placeholder="Search books, authors, genres',
            html=False
        )
        self.assertContains(resp, 'class="search-card shadow"', html=False)

        # Check dropdown options
        self.assertContains(
            resp,
            '<option value="all">All</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="title">Title</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="author">Author</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="subject">Genre</option>',
            html=False
            )
