from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

PER_PAGE = 12


def _fake_books(n=PER_PAGE, prefix="B"):
    """Minimal template data: id, title, authors, thumbnail"""
    return [
        {"id": f"{prefix}{i}", "title": f"Title {i}", "authors": "A", "thumbnail": ""}
        for i in range(n)
    ]


class BookSearchPaginationTests(TestCase):
    """ Tests for book_search view pagination logic"""
    def setUp(self):
        self.url = reverse("book_search")

        # Patches for activity lookups used in the view
        self.p_status = patch("books.views.statuses_map_for", return_value={})
        self.p_rating = patch("books.views.ratings_map_for", return_value={})
        self.p_avg = patch("books.views.get_average_rating", return_value=0)
        self.p_num = patch("books.views.get_number_of_ratings", return_value=0)

        self.p_status.start()
        self.p_rating.start()
        self.p_avg.start()
        self.p_num.start()

        self.addCleanup(self.p_status.stop)
        self.addCleanup(self.p_rating.stop)
        self.addCleanup(self.p_avg.stop)
        self.addCleanup(self.p_num.stop)

    @patch("books.views.search_google_books")
    def test_book_search_pagination_first_page(self, mock_search):
        """Verifies that page 1 uses start_index=0."""
        mock_search.return_value = (_fake_books(), 30)

        resp = self.client.get(self.url, {"q": "django", "field": "all", "page": 1})
        self.assertEqual(resp.status_code, 200)

        # Assert the call used start_index=0, max_results=12
        mock_search.assert_called_with("django", start_index=0, max_results=PER_PAGE)

        # Context has a Page with the first-item index 1 and last-item index 12
        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.start_index(), 1)
        self.assertEqual(page_obj.end_index(), PER_PAGE)

    @patch("books.views.search_google_books")
    def test_book_search_pagination_second_page(self, mock_search):
        """Verifies that page 2 uses start_index=12."""
        mock_search.return_value = (_fake_books(), 30)

        resp = self.client.get(self.url, {"q": "python", "field": "all", "page": 2})
        self.assertEqual(resp.status_code, 200)

        # start_index should be (2 - 1) * 12 = 12
        mock_search.assert_called_with("python", start_index=PER_PAGE, max_results=PER_PAGE)

        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.number, 2)
        # With total=30, page 2 covers items 13–24
        self.assertEqual(page_obj.start_index(), PER_PAGE + 1)
        self.assertEqual(page_obj.end_index(), PER_PAGE * 2)

    @patch("books.views.search_google_books")
    def test_book_search_pagination_context_variables(self, mock_search):
        """Tests that all pagination template variables are set correctly."""
        total = 30
        mock_search.return_value = (_fake_books(), total)

        resp = self.client.get(self.url, {"q": "testing", "field": "all", "page": 1})
        self.assertEqual(resp.status_code, 200)

        # Context variables for the template
        self.assertIn("page_obj", resp.context)
        self.assertIn("paginator", resp.context)
        self.assertIn("is_paginated", resp.context)
        self.assertIn("page_range", resp.context)

        page_obj = resp.context["page_obj"]
        paginator = resp.context["paginator"]

        self.assertTrue(resp.context["is_paginated"])
        self.assertEqual(paginator.count, total)
        self.assertEqual(paginator.per_page, PER_PAGE)
        self.assertGreaterEqual(len(resp.context["page_range"]), 1)

        # The view replaces object_list with books for rendering
        self.assertEqual(len(list(page_obj.object_list)), PER_PAGE)


class GenreBrowsingTests(TestCase):
    """
    Tests for genre links on home page
    and their interaction with book_search pagination.
    """
    def setUp(self):
        self.home_url = reverse("home")
        self.search_url = reverse("book_search")

        # View patches
        self.p_status = patch("books.views.statuses_map_for", return_value={})
        self.p_rating = patch("books.views.ratings_map_for", return_value={})
        self.p_avg = patch("books.views.get_average_rating", return_value=0)
        self.p_num = patch("books.views.get_number_of_ratings", return_value=0)

        self.p_status.start()
        self.p_rating.start()
        self.p_avg.start()
        self.p_num.start()

        self.addCleanup(self.p_status.stop)
        self.addCleanup(self.p_rating.stop)
        self.addCleanup(self.p_avg.stop)
        self.addCleanup(self.p_num.stop)

    def test_home_page_genre_links_format(self):
        """
        Confirms genre links have the correct URL structure:
        /book_search?field=subject&q=<urlencoded-subject>
        """
        resp = self.client.get(self.home_url)
        self.assertEqual(resp.status_code, 200)

        # Spot-check
        self.assertInHTML(
            '<a href="{}?field=subject&amp;q=science%20fiction" class="stretched-link" aria-label="Browse Sci-Fi"></a>'.format(self.search_url),  # noqa: E501
            resp.content.decode("utf-8"),
        )
        self.assertInHTML(
            '<a href="{}?field=subject&amp;q=mystery" class="stretched-link" aria-label="Browse Mystery"></a>'.format(self.search_url),  # noqa: E501
            resp.content.decode("utf-8"),
        )

    @patch("books.views.search_google_books")
    def test_genre_tile_redirects_to_search_with_pagination(self, mock_search):
        """
        Tests that clicking a genre tile (subject) hits book_search and paginates.
        """
        mock_search.return_value = (_fake_books(), 40)

        # Simulate clicking the "Sci-Fi" tile (subject=science fiction), page 1
        resp = self.client.get(self.search_url, {"field": "subject", "q": "science fiction", "page": 1})
        self.assertEqual(resp.status_code, 200)
        mock_search.assert_called_with("subject:science fiction", start_index=0, max_results=PER_PAGE)

    @patch("books.views.search_google_books")
    def test_genre_tile_second_page_maintains_genre_filter(self, mock_search):
        """
        Verifies that pagination preserves the genre filter (field & q) on subsequent pages.
        """
        total = 40
        mock_search.return_value = (_fake_books(), total)

        resp = self.client.get(self.search_url, {"field": "subject", "q": "mystery", "page": 2})
        self.assertEqual(resp.status_code, 200)

        # start_index should reflect page 2
        mock_search.assert_called_with("subject:mystery", start_index=PER_PAGE, max_results=PER_PAGE)

        html = resp.content.decode("utf-8")

        # Prev/First keep the subject filter
        self.assertIn('href="?field=subject&amp;q=mystery&amp;page=1"', html)
        # Next/Last keep the subject filter too
        self.assertIn('href="?field=subject&amp;q=mystery&amp;page=3"', html)

        # Numbered page links for other pages preserve params
        self.assertIn('href="?field=subject&amp;q=mystery&amp;page=1"', html)
        self.assertIn('href="?field=subject&amp;q=mystery&amp;page=3"', html)

        # Current page (2) is an active <span>, not a link
        self.assertIn('<li class="page-item active"><span class="page-link">2</span></li>', html)
        self.assertNotIn('href="?field=subject&amp;q=mystery&amp;page=2"', html)
