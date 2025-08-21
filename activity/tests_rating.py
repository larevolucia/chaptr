""" Tests for rating activity views"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from books.models import Book
from .models import Rating, ReadingStatus

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

    def test_authenticated_users_can_update_a_book_rating(self):
        """Test that authenticated users can update their book rating."""
        self.client.force_login(self.user)
        Rating.objects.create(
            user=self.user,
            book=self.book,
            rating=2
        )

        response = self.client.post(
            self.url,
            data={"rating": 5},
            follow=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.detail_url)

        r = Rating.objects.get(user=self.user, book=self.book)
        self.assertEqual(r.rating, 5)  # updated, not duplicated
        self.assertEqual(
            Rating.objects.filter(
                user=self.user,
                book=self.book
            ).count(),
            1
        )

    def test_authenticated_users_can_remove_a_book_rating(self):
        """Test that authenticated users can remove their book rating."""
        self.client.force_login(self.user)
        Rating.objects.create(
            user=self.user,
            book=self.book,
            rating=2
        )

        response = self.client.post(
            self.url,
            data={"rating": 0},
            follow=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.detail_url)

        self.assertFalse(
            Rating.objects.filter(
                user=self.user,
                book=self.book
            ).exists()
        )

    def test_user_can_rate_book_with_no_reading_status(self):
        """
        Test that authenticated users can rate a book
        with no reading status.
        """
        self.client.force_login(self.user)
        # Ensure no reading status exists
        self.assertFalse(
            ReadingStatus.objects.filter(
                user=self.user,
                book=self.book
            ).exists()
        )

        # post rating
        response = self.client.post(self.url, data={"rating": 5}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.detail_url)

        # created?
        self.assertTrue(
            Rating.objects.filter(
                user=self.user, book=self.book, rating=5
                ).exists()
        )

        rs = ReadingStatus.objects.get(user=self.user, book=self.book)
        self.assertEqual(rs.status, ReadingStatus.Status.READ)

    def test_can_rate_regardless_of_existing_reading_status_and_preserve_it(self):
        """
        If the user already has any reading status (TO_READ/READING/READ),
        rating should still succeed and the existing status should remain unchanged.
        """
        self.client.force_login(self.user)
        # Start with TO_READ
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book,
            status=ReadingStatus.Status.TO_READ
        )

        response = self.client.post(self.url, data={"rating": 3}, follow=False)

        # Check response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.detail_url)
        # Rating exists
        self.assertTrue(
            Rating.objects.filter(
                user=self.user,
                book=self.book,
                rating=3
            ).exists()
        )
        # Status unchanged (signal should NOT override an existing status)
        rs = ReadingStatus.objects.get(
            user=self.user,
            book=self.book
            )
        self.assertEqual(rs.status, ReadingStatus.Status.TO_READ)
