"""
Tests for the ReadingStatus functionality.
"""
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from .models import ReadingStatus

User = get_user_model()


class ReadingStatusUITests(TestCase):
    """Tests for the ReadingStatus functionality."""
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass12345"
        )
        self.book = Book.objects.create(id="VOL123", title="Dune")  # noqa: E501 pylint: disable=no-member

        self.detail_url = reverse("book_detail", args=[self.book.pk])
        self.add_status_url = reverse("set_reading_status", args=[self.book.pk])  # noqa: E501

    @patch('requests.get')
    def test_anonymous_user_sees_login_button(self, mock_requests_get):
        """Test that anonymous users see log in button."""
        # Mock the HTTP response from Google Books API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': 'VOL123',
            'volumeInfo': {
                'title': 'Dune',
                'authors': ['Frank Herbert'],
                'description': 'Test description',
                'imageLinks': {'thumbnail': 'http://example.com/image.jpg'}
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        url = reverse("book_detail", args=[self.book.pk])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Log in to add", html=False)
        self.assertContains(resp, reverse("account_login"), html=False)

    def test_all_valid_status_choices(self):
        """Test all valid status choices can be set"""
        self.client.force_login(self.user)
        valid_statuses = ["TO_READ", "READING", "READ"]

        for status in valid_statuses:
            with self.subTest(status=status):
                user_status = {"status": status}
                response = self.client.post(self.add_status_url, data=user_status)  # noqa: E501

                self.assertEqual(response.status_code, 302)
                reading_status = ReadingStatus.objects.get(
                    user=self.user, book=self.book
                )
                self.assertEqual(reading_status.status, status)

    def test_add_status_creates_record_for_authenticated_user(self):
        """
        Clicking the button when authenticated
        creates the record with the correct status
        """
        self.client.force_login(self.user)
        user_status = {"status": "TO_READ"}
        resp = self.client.post(self.add_status_url, data=user_status, follow=False)  # noqa: F841 E501 pylint: disable=unused-variable

        self.assertTrue(
            ReadingStatus.objects.filter(
                user=self.user, book=self.book, status="TO_READ"
            ).exists()
        )

    def test_unauthenticated_user_redirected_to_login(self):
        """Unauthenticated users should be redirected to login page"""
        user_status = {"status": "TO_READ"}
        response = self.client.post(self.add_status_url, data=user_status)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        # Ensure no reading status was created
        self.assertFalse(
            ReadingStatus.objects.filter(book=self.book).exists()
        )
