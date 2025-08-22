"""
Tests for the Review functionality.
"""
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from books.models import Book
from activity.models import Review, ReadingStatus

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

        response = self.client.post(
            self.add_review_url,
            {"content": "Great read!"}
            )
        # should redirect back to book_detail
        self.assertRedirects(response, self.detail_url)

        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.get()
        self.assertEqual(review.user, self.alice)
        self.assertEqual(review.book_id, self.book_id)
        self.assertEqual(review.content, "Great read!")

    @patch("books.views.fetch_book_by_id")
    def test_book_detail_displays_reviews(self, mock_fetch):
        """Test that the book detail view displays reviews."""
        mock_fetch.return_value = self.fetch_stub
        # Create a review by Bob
        Review.objects.create(user=self.bob, book_id=self.book_id, content="Loved it!")

        self.login(self.alice)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Reviews")
        self.assertContains(response, "Loved it!")
        self.assertContains(response, "bob")

    @patch("books.views.fetch_book_by_id")
    def test_anonymous_sees_login_message_no_form(self, mock_fetch):
        """Test that an anonymous user sees a login prompt without a form."""
        mock_fetch.return_value = self.fetch_stub
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, ">Log in</a> to leave and read reviews")
        self.assertNotContains(response, '<form id="reviewForm"', html=False)

    @patch("books.views.fetch_book_by_id")
    def test_authenticated_user_without_review_sees_form(self, mock_fetch):
        """
        Test that an authenticated user 
        without a review sees the review form.
        """
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        # Form textarea for `content`
        self.assertContains(response, '<textarea', html=False)
        # Action points to the add_review URL
        self.assertContains(response, f'action="{self.add_review_url}"')

    @patch("books.views.fetch_book_by_id")
    def test_user_can_edit_review_without_creating_duplicate(self, mock_fetch):
        """
        Test that a user can edit their review 
        without creating a duplicate.
        """
        mock_fetch.return_value = self.fetch_stub
        # Create an initial review
        Review.objects.create(user=self.alice, book_id=self.book_id, content="OK book")

        self.login(self.alice)

        # Edit the existing review
        response = self.client.post(self.add_review_url, {"content": "Actually, fantastic"})
        self.assertRedirects(response, self.detail_url)

        # Still exactly one review for (user, book)
        self.assertEqual(Review.objects.filter(user=self.alice, book_id=self.book_id).count(), 1)
        r = Review.objects.get(user=self.alice, book_id=self.book_id)
        self.assertEqual(r.content, "Actually, fantastic")

    @patch("books.views.fetch_book_by_id")
    def test_review_creates_read_status_when_none_exists(self, mock_fetch):
        """
        Posting a review creates READ status if none exists
        """
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        # No status yet → posting a review should create READ
        self.assertFalse(
            ReadingStatus.objects.filter(user=self.alice, book_id=self.book_id).exists()
        )
        response = self.client.post(self.add_review_url, {"content": "Great read!"})
        self.assertRedirects(response, self.detail_url)

        rs = ReadingStatus.objects.get(user=self.alice, book_id=self.book_id)
        self.assertEqual(rs.status, ReadingStatus.Status.READ)

    @patch("books.views.fetch_book_by_id")
    def test_review_respects_existing_read_status(self, mock_fetch):
        """
        If a status already exists, posting a review should NOT
        override it to READ.
        """
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        # Create pre-existing non-READ status
        ReadingStatus.objects.create(
            user=self.alice,
            book_id=self.book_id,  # <-- use book_id, not book=
            status=ReadingStatus.Status.READING,
        )

        # Check current status
        rs = ReadingStatus.objects.get(user=self.alice, book_id=self.book_id)
        self.assertEqual(rs.status, ReadingStatus.Status.READING)

        # Post a review
        Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="Halfway through."
        )

        # Status should remain READING
        rs = ReadingStatus.objects.get(user=self.alice, book_id=self.book_id)
        self.assertEqual(rs.status, ReadingStatus.Status.READING)
