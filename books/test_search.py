from django.test import TestCase, RequestFactory
from unittest.mock import patch
from books.views import (
    build_q,
    book_search,
)


class BuildQTests(TestCase):
    def test_build_q_with_field_author(self):
        q = build_q("emily bronte", "author")
        self.assertEqual(q, "inauthor:emily bronte")

    def test_build_q_preserves_existing_operator_even_if_field_differs(self):
        q = build_q("intitle:wuthering heights", "author")
        self.assertEqual(q, "intitle:wuthering heights")

    def test_build_q_all_keeps_plain_text(self):
        q = build_q("wuthering heights", "all")
        self.assertEqual(q, "wuthering heights")

    def test_build_q_subject_applies_operator(self):
        q = build_q("poetry", "subject")
        self.assertEqual(q, "subject:poetry")

    def test_build_q_empty_returns_empty(self):
        q = build_q("", "author")
        self.assertEqual(q, "")


class BookSearchViewTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    @patch("books.views.search_google_books")
    def test_book_search_uses_built_query(self, mock_search):
        mock_search.return_value = []
        req = self.rf.get("/books/search", {"field": "author", "q": "emily bronte"})
        resp = book_search(req)
        self.assertEqual(resp.status_code, 200)
        # ensure build_q result was used
        called_q = mock_search.call_args.args[0]
        self.assertEqual(called_q, "inauthor:emily bronte")
