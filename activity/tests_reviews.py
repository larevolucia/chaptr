"""
Tests for the Review functionality.
"""
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from books.models import Book
from activity.models import Review

User = get_user_model()


class ReviewFlowTests(TestCase):
    """Test the review flow for books."""
    def setUp(self):
        self.client = Client()
        self.book_id = "TESTBOOK123"
        # Minimal Book row to satisfy FKs in activity.Review
        Book.objects.create(id=self.book_id, title="Stub Title")

        # URLs from your apps
        self.detail_url = reverse("book_detail", args=[self.book_id])
        self.add_review_url = reverse("add_review", args=[self.book_id])

        self.fetch_stub = {"id": self.book_id, "title": "Stub Title"}

        # Users
        self.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass12345"
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass12345"
        )

    def login(self, user):
        """Helper to log in a user."""
        self.client.login(username=user.username, password="pass12345")

    @patch("books.views.fetch_book_by_id")
    def test_user_can_create_review(self, mock_fetch):
        """Test that a logged-in user can create a review."""
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        resp = self.client.post(
            self.add_review_url,
            {"content": "Great read!"}
            )
        # should redirect back to book_detail
        self.assertRedirects(resp, self.detail_url)

        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.get()
        self.assertEqual(review.user, self.alice)
        self.assertEqual(review.book_id, self.book_id)
        self.assertEqual(review.content, "Great read!")
