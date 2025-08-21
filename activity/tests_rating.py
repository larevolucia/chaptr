""" Tests for rating activity views"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from books.models import Book
from .models import Rating

User = get_user_model()


class RatingViewTests(TestCase):
    """Test the rating views."""
    def setUp(self):
        # Basic user + book
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="secret123",
        )
        # Use Google Books-like id
        self.book = Book.objects.create(id="gbook-123", title="Test Book")

        self.url = reverse("set_rating", args=[self.book.id])
        self.detail_url = reverse("book_detail", args=[self.book.id])

    def test_unauthenticated_users_redirect_to_login(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.post(self.url, data={"rating": 5}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        # Ensure no rating was created
        self.assertFalse(
            Rating.objects.filter(book=self.book).exists()
        )

    def test_rating_creates_record_for_authenticated_user(self):
        """Test that posting a rating creates a Rating object."""
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={"rating": 5}, follow=False)

        # created?
        self.assertTrue(
            Rating.objects.filter(
                user=self.user, book=self.book, rating=5
                ).exists()
        )

        # redirected where expected, without fetching the target
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.detail_url)
