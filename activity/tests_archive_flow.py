from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from books.models import Book
from activity.models import ReadingStatus, Rating, Review

User = get_user_model()


class ArchiveOnStatusRemovalTests(TestCase):
    """ Tests that setting reading status to NONE archives ratings and reviews."""
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pw")
        self.book = Book.objects.create(id="B1", title="T")
        self.url = reverse("set_reading_status", args=[self.book.id])
        self.detail = reverse("book_detail", args=[self.book.id])

    def test_status_none_archives_rating_and_review(self):
        """ Setting status to NONE deletes status and archives ratings and reviews."""
        self.client.login(username="u", password="pw")
        ReadingStatus.objects.create(user=self.user, book=self.book, status=ReadingStatus.Status.READING)
        Rating.objects.create(user=self.user, book=self.book, rating=4)
        Review.objects.create(user=self.user, book=self.book, content="hi")

        resp = self.client.post(self.url, {"status": "NONE", "next": self.detail})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(ReadingStatus.objects.filter(user=self.user, book=self.book).exists())

        r = Rating.objects.get(user=self.user, book=self.book)
        v = Review.objects.get(user=self.user, book=self.book)
        self.assertTrue(r.is_archived)
        self.assertTrue(v.is_archived)
        self.assertIsNotNone(r.archived_at)
        self.assertIsNotNone(v.archived_at)


class UnarchiveOnNewRatingTests(TestCase):
    """ Tests that posting a new rating unarchives any archived rating and creates a default status if missing."""
    def setUp(self):
        self.user = User.objects.create_user(username="u2", password="pw")
        self.book = Book.objects.create(id="B2", title="T2")
        self.url = reverse("set_rating", args=[self.book.id])
        self.detail = reverse("book_detail", args=[self.book.id])

    def test_post_rating_unarchives_and_creates_status(self):
        self.client.login(username="u2", password="pw")
        Rating.objects.create(user=self.user, book=self.book, rating=2, is_archived=True, archived_at=timezone.now())

        resp = self.client.post(self.url, {"rating": "5", "next": self.detail})
        self.assertEqual(resp.status_code, 302)

        # status exists (default READ when missing)
        self.assertTrue(ReadingStatus.objects.filter(user=self.user, book=self.book).exists())

        # rating revived & updated
        r = Rating.objects.get(user=self.user, book=self.book)
        self.assertFalse(r.is_archived)
        self.assertEqual(r.rating, 5)


class DetailHidesArchivedReviewsTests(TestCase):
    """ Tests that archived reviews are not shown on the book detail page."""
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pw")

    def login(self, who="user"):
        """ Helper to login as one of the two users."""
        user = self.user if who == "user" else self.other
        self.client.login(username=user.username, password="pw")
        return user

    @patch("books.views.fetch_book_by_id")
    def test_archived_reviews_hidden_from_detail(self, mock_fetch):
        """ Archived reviews should not appear on book detail page."""
        self.login("user")
        mock_fetch.return_value = {"id": "B4", "title": "T4"}
        book = Book.objects.create(id="B4", title="T4")

        # one archived, one active
        Review.objects.create(user=self.user, book=book, content="OLD", is_archived=True)
        Review.objects.create(user=self.user, book=book, content="NEW", is_archived=False)

        url = reverse("book_detail", args=[book.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "NEW")
        self.assertNotContains(resp, "OLD")
