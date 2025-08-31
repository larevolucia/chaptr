from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

from books.models import Book
from activity.models import ReadingStatus, Review

User = get_user_model()


class LibraryAndReviewsTests(TestCase):
    """ Tests for removing books from library and deleting reviews."""
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pw")
        self.other = User.objects.create_user(username="u2", password="pw")
        self.book = Book.objects.create(
            id="TEST-BOOK-1", title="Test Book", authors=["A One"]
        )

    def login(self, who="user"):
        """ Helper to login as one of the two users."""
        user = self.user if who == "user" else self.other
        self.client.login(username=user.username, password="pw")
        return user

    def test_remove_from_library_from_details_deletes_and_redirects(self):
        """Remove from Library (details page)"""
        self.login("user")
        # seed a status
        ReadingStatus.objects.create(user=self.user, book=self.book, status="READING")

        url = reverse("set_reading_status", args=[self.book.id])
        next_url = reverse("book_detail", args=[self.book.id])

        resp = self.client.post(url, data={"status": "NONE", "next": next_url})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], next_url)

        self.assertFalse(
            ReadingStatus.objects.filter(user=self.user, book=self.book).exists()
        )

        # confirm the success flash
        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Removed your reading status.", msgs)

    def test_delete_review_owner_only(self):
        """ Delete review (owner)"""
        self.login("user")
        review = Review.objects.create(user=self.user, book=self.book, content="ok")

        url = reverse("delete_review", args=[self.book.id, review.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("book_detail", args=[self.book.id]))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Your review was deleted.", msgs)
