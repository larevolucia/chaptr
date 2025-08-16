from django.test import TestCase
from books.views import build_q


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
