"""
Tests for the Review functionality.
"""
from unittest.mock import patch
from django.contrib.messages import get_messages
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

    def delete_review_url(self, review_id: int) -> str:
        """Helper to get delete_review URL for a given review_id. """
        return reverse("delete_review", args=[self.book_id, review_id])

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
        Review.objects.create(
            user=self.bob,
            book_id=self.book_id,
            content="Loved it!"
        )

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

        self.assertContains(response, 'id="review-login-prompt"')
        self.assertNotContains(response, 'id="reviewForm"')

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
        Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="OK book"
            )

        self.login(self.alice)

        # Edit the existing review
        response = self.client.post(
            self.add_review_url, {"content": "Actually, fantastic"}
        )
        self.assertRedirects(response, self.detail_url)

        # Still exactly one review for (user, book)
        self.assertEqual(
            Review.objects.filter(
                user=self.alice,
                book_id=self.book_id
                ).count(), 1
        )
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
            ReadingStatus.objects.filter(
                user=self.alice,
                book_id=self.book_id
                ).exists()
        )
        response = self.client.post(
            self.add_review_url, {"content": "Great read!"}
        )
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

    def test_user_can_delete_own_review(self):
        """
        Test that a user can delete their own review.
        """
        self.login(self.alice)
        # Create a review to delete
        review = Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="This book was okay."
        )
        delete_url = self.delete_review_url(review.id)
        response = self.client.post(delete_url)
        self.assertRedirects(response, self.detail_url)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    @patch("books.views.fetch_book_by_id")
    def test_delete_button_visible_only_for_owner(self, mock_fetch):
        """
        The delete control should be visible
        for the current user's own review only.
        """
        mock_fetch.return_value = self.fetch_stub

        # Two reviews: Alice's and Bob's
        alice_rev = Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="Mine"
        )
        bobs_rev = Review.objects.create(
            user=self.bob,
            book_id=self.book_id,
            content="Not mine"
        )

        # Alice sees her delete control (in "my_review" block)
        self.login(self.alice)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, 200)
        # delete action for Alice's review should be present
        self.assertContains(resp, self.delete_review_url(alice_rev.id))
        # delete action for Bob's review should NOT be present
        self.assertNotContains(resp, self.delete_review_url(bobs_rev.id))

        # Bob logs in: he should see only his own delete control
        self.client.logout()
        self.login(self.bob)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.delete_review_url(bobs_rev.id))
        self.assertNotContains(resp, self.delete_review_url(alice_rev.id))

    @patch("books.views.fetch_book_by_id")
    def test_delete_confirmation_modal_markup_present(self, mock_fetch):
        """
        The book detail page should render a modal for delete confirmation,
        and delete buttons should point to it.
        """
        mock_fetch.return_value = self.fetch_stub
        # Alice review
        review = Review.objects.create(user=self.alice, book_id=self.book_id, content="Mine")

        self.login(self.alice)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

        # Modal markup is present
        self.assertContains(response, 'id="confirmDeleteModal"')
        self.assertContains(response, 'class="modal fade"')

        # Delete button points to the modal
        self.assertContains(response, 'data-bs-toggle="modal"')
        self.assertContains(response, 'data-bs-target="#confirmDeleteModal"')

    @patch("books.views.fetch_book_by_id")
    def test_delete_shows_success_message(self, mock_fetch):
        """
        After a successful delete POST, a success message is flashed.
        """
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        rev = Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="Delete me"
        )
        url = self.delete_review_url(rev.id)

        resp = self.client.post(url, follow=True)
        self.assertRedirects(resp, self.detail_url)

        # Check messages framework
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Your review was deleted.", messages)

    @patch("books.views.fetch_book_by_id")
    def test_delete_removes_record_from_db(self, mock_fetch):
        """
        A successful POST to delete removes the Review row.
        """
        mock_fetch.return_value = self.fetch_stub
        self.login(self.alice)

        rev = Review.objects.create(
            user=self.alice,
            book_id=self.book_id,
            content="Delete me"
            )
        url = self.delete_review_url(rev.id)

        self.assertTrue(Review.objects.filter(pk=rev.pk).exists())
        resp = self.client.post(url)
        self.assertRedirects(resp, self.detail_url)
        self.assertFalse(Review.objects.filter(pk=rev.pk).exists())
