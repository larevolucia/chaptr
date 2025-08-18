"""Tests for the books app views and helpers.

Covers:
- Query building via `build_q`.
- Search view wiring to `search_google_books`.
- Google Books list search happy/empty paths.
- Single volume fetch mapping and 404 behavior.
- Detail view rendering and caching behavior.

Notes:
- External HTTP calls are patched.
- Cache is cleared where needed to avoid cross-test state.
"""
import os
from unittest.mock import patch, Mock
from requests import HTTPError
from django.urls import reverse
from django.core.cache import cache
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from books.views import (
    build_q,
    book_search,
    search_google_books,
    fetch_book_by_id,
    book_detail
)

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
        mock_search.return_value = []
        req = self.rf.get("/books/search", {"field": "author", "q": "emily bronte"})  # noqa: E501
        resp = book_search(req)
        self.assertEqual(resp.status_code, 200)
        # ensure build_q result was used
        called_q = mock_search.call_args.args[0]
        self.assertEqual(called_q, "inauthor:emily bronte")


class SearchGoogleBooksTests(TestCase):
    """Integration tests for the Google Books API search functionality."""
    @patch.dict(os.environ, {"GOOGLE_BOOKS_API_KEY": "fake-key"}, clear=False)
    @patch("books.views.requests.get")
    def test_returns_parsed_list_on_200(self, mock_get):
        """Test that a successful API call returns a parsed list."""
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {
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

        results = search_google_books("inauthor:emily bronte")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "X")
        self.assertEqual(results[0]["authors"], "A")
        self.assertEqual(results[0]["title"], "T")
        self.assertEqual(results[0]["thumbnail"], "http://t")
        self.assertEqual(results[1]["id"], "Y")
        self.assertEqual(results[1]["authors"], "B")
        self.assertEqual(results[1]["title"], "U")
        self.assertEqual(results[1]["thumbnail"], "http://u")

    @patch.dict(os.environ, {"GOOGLE_BOOKS_API_KEY": "fake-key"}, clear=False)
    @patch("books.views.requests.get")
    def test_non_200_or_exception_returns_empty(self, mock_get):
        """Test that non-200 responses or exceptions return an empty list."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = HTTPError("500")
        mock_get.return_value = mock_resp
        self.assertEqual(search_google_books("X"), [])


class FetchBookByIdTests(TestCase):
    """Integration tests for the fetch_book_by_id function."""
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()

    @patch("books.views.requests.get")
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

    @patch("books.views.requests.get")
    def test_fetch_book_by_id_404_on_non_200(self, mock_get):
        """Test that fetch_book_by_id raises Http404 on non-200."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = HTTPError("404")
        mock_get.return_value = mock_resp
        with self.assertRaises(Http404):
            fetch_book_by_id("nonexistent")


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
        self.assertIn(b"http://thumb", resp.content)
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
        book_search_url = reverse("book-search")
        self.assertContains(resp, f'action="{book_search_url}"', html=False)

        # Check for search form structure
        self.assertContains(resp, 'placeholder="Search books, authors, genres', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, 'class="search-card shadow"', html=False)

        # Check dropdown options
        self.assertContains(resp, '<option value="all">All</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="title">Title</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="author">Author</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="subject">Genre</option>', html=False)  # noqa: E501 pylint: disable=line-too-long


class HomeViewTests(TestCase):
    """Tests for the home page view and template."""
    def setUp(self):
        # Create a test user for authentication tests.
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="S3curepass!123"
        )

    def test_home_view_renders(self):
        """Test that the home page loads without errors."""
        url = reverse("home")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that home view uses the correct template."""
        url = reverse("home")
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'books/home.html')

    def test_home_page_extends_base_template(self):
        """Test that essential base template elements are present."""
        url = reverse("home")
        resp = self.client.get(url)

        # Check for base template elements
        self.assertContains(resp, "NextChaptr", html=False)  # Brand name
        self.assertContains(resp, "© 2025 NextChaptr", html=False)  # Footer
        self.assertContains(resp, "Skip to main content", html=False)  # A11y

    def test_search_form_inclusion(self):
        """Test that the search form is included in the header."""
        url = reverse("home")
        resp = self.client.get(url)

        # Check for search form elements based on search_form.html
        self.assertContains(resp, 'name="q"', html=False)
        self.assertContains(resp, 'name="field"', html=False)
        self.assertContains(resp, 'role="search"', html=False)
        self.assertContains(resp, 'aria-label="Site search"', html=False)

        # Check for specific form action
        self.assertContains(resp, 'action="/search/"', html=False)

        # Check for search form structure
        self.assertContains(resp, 'placeholder="Search books, authors, genres', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, 'class="search-card shadow"', html=False)

        # Check dropdown options
        self.assertContains(resp, '<option value="all">All</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="title">Title</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="author">Author</option>', html=False)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, '<option value="subject">Genre</option>', html=False)  # noqa: E501 pylint: disable=line-too-long

    def test_anonymous_user_sees_auth_links(self):
        """Test that anonymous users see sign up and log in links."""
        url = reverse("home")
        resp = self.client.get(url)

        self.assertContains(resp, "Sign up", html=False)
        self.assertContains(resp, "Log in", html=False)

        self.assertContains(resp, reverse("account_signup"), html=False)
        self.assertContains(resp, reverse("account_login"), html=False)

    def test_authenticated_user_sees_welcome_and_logout(self):
        """Test that logged-in users see welcome message and logout link."""
        self.client.force_login(self.user)

        url = reverse("home")
        resp = self.client.get(url)

        self.assertContains(resp, "Hi, testuser", html=False)

        self.assertContains(resp, "Log out", html=False)
        self.assertContains(resp, reverse("account_logout"), html=False)

        self.assertNotContains(resp, "Sign up", html=False)
        self.assertNotContains(resp, "Log in", html=False)
