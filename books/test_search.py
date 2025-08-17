import os
from unittest.mock import patch, Mock
from requests import HTTPError
from django.core.cache import cache
from django.test import TestCase, RequestFactory
from books.views import (
    build_q,
    book_search,
    search_google_books,
    fetch_book_by_id,
    book_detail
)


REALISTIC_DETAIL_JSON = {
    "id": "AkVWPbrWKGEC",
    "volumeInfo": {
        "title": "The Poems of Emily Bronte",
        "subtitle": "A Nice Subtitle",
        "authors": ["Emily Brontë"],
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
        req = self.rf.get("/books/search", {"field": "author", "q": "emily bronte"})  # noqa: E501
        resp = book_search(req)
        self.assertEqual(resp.status_code, 200)
        # ensure build_q result was used
        called_q = mock_search.call_args.args[0]
        self.assertEqual(called_q, "inauthor:emily bronte")


class SearchGoogleBooksTests(TestCase):
    @patch.dict(os.environ, {"GOOGLE_BOOKS_API_KEY": "fake-key"}, clear=False)
    @patch("books.views.requests.get")
    def test_returns_parsed_list_on_200(self, mock_get):
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
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = HTTPError("500")
        mock_get.return_value = mock_resp
        self.assertEqual(search_google_books("X"), [])


class FetchBookByIdTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("books.views.requests.get")
    def test_fetch_book_by_id_success_maps_fields(self, mock_get):
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = REALISTIC_DETAIL_JSON
        mock_get.return_value = mock_resp

        data = fetch_book_by_id("AkVWPbrWKGEC")
        self.assertEqual(data["id"], "AkVWPbrWKGEC")
        self.assertEqual(data["title"], "The Poems of Emily Bronte")
        self.assertEqual(data["subtitle"], "A Nice Subtitle")
        self.assertEqual(data["authors"], "Emily Brontë")
        self.assertEqual(data["publisher"], "Rowman & Littlefield")
        self.assertEqual(data["publishedDate"], "1992-01-01")
        self.assertEqual(data["pageCount"], 206)
        self.assertIn("Poetry", data["categories"])
        self.assertEqual(data["description"], "Some description.")
        self.assertTrue(data["thumbnail"].startswith("http"))
        self.assertEqual(data["previewLink"], "http://example.test/preview")
