""" Tests for the library app views and functionality."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.messages import get_messages

# Create your tests here.

from books.models import Book
from activity.models import ReadingStatus

User = get_user_model()


class LibraryViewTests(TestCase):
    """ Test the library views """
    def setUp(self):
        # Create a user we can log in with
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="pass1234"
        )
        self.book_to_read = Book.objects.create(
            id="to-read",
            title="To Read Book"
        )
        self.book_reading = Book.objects.create(
            id="reading",
            title="Reading Book"
            )
        self.book_read = Book.objects.create(
            id="read",
            title="Read Book"
            )

    def set_book_to_read(self):
        """ Log a book with 'to read' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book_to_read,
            status=ReadingStatus.Status.TO_READ
        )

    def set_book_reading(self):
        """ Log a book with 'reading' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book_reading,
            status=ReadingStatus.Status.READING
        )

    def set_book_read(self):
        """ Log a book with 'read' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book_read,
            status=ReadingStatus.Status.READ
        )

    def set_books_statuses(self):
        """ Log three books with different statuses for the user."""
        self.client.login(username="alice", password="pass1234")
        self.set_book_to_read()
        self.set_book_reading()
        self.set_book_read()

    def test_navbar_links_visible_only_when_authenticated(self):
        """
        Navbar (in base.html) shows user
        dropdown items only for logged-in users.
        """
        response_anon = self.client.get(reverse("library"), follow=True)
        self.assertEqual(response_anon.status_code, 200)
        self.assertNotContains(response_anon, "Library")
        self.assertNotContains(response_anon, "Browse")
        self.assertNotContains(response_anon, "Sign out")

        self.client.login(username="alice", password="pass1234")
        response_auth = self.client.get(reverse("library"))
        self.assertContains(response_auth, "Library")
        self.assertContains(response_auth, "Browse")
        self.assertContains(response_auth, "Sign out")

    def test_unauthenticated_user_is_redirected_to_login(self):
        """
        Unauthenticated users should not see the library page.
        The @login_required decorator redirects to LOGIN_URL with ?next=...
        """
        url = reverse("library")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response["Location"])
        self.assertIn("?next=", response["Location"])

    def test_authenticated_user_can_access_library(self):
        """
        Authenticated users should be able to access the library page.
        """
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("library"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/library.html")
        self.assertContains(response, "Your Library")

    def test_library_page_no_books(self):
        """
        If the user has no books in their library, they should see a message.
        """
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("library"))
        self.assertContains(response, 'data-testid="empty-library"')

    def test_library_page_with_books(self):
        """
        If the user has books in their library,
        they should see them organized by status.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_books_statuses()

        response = self.client.get(reverse("library"))
        self.assertContains(response, 'data-testid="library-table"')
        self.assertNotContains(response, 'data-testid="empty-library"')

    def test_library_page_with_only_to_read_book(self):
        """
        If the user has only books on their to-read list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_to_read()

        response = self.client.get(reverse("library"))
        self.assertContains(response, 'data-testid="library-table"')
        self.assertNotContains(response, 'data-testid="empty-library"')

    def test_library_page_with_only_reading_book(self):
        """
        If the user has only books on their reading list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_reading()

        response = self.client.get(reverse("library"))
        self.assertContains(response, 'data-testid="library-table"')
        self.assertNotContains(response, 'data-testid="empty-library"')

    def test_library_page_with_only_read_book(self):
        """
        If the user has only books on their reading list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_read()

        response = self.client.get(reverse("library"))
        self.assertContains(response, 'data-testid="library-table"')
        self.assertNotContains(response, 'data-testid="empty-library"')

    def test_each_book_links_to_its_detail_page(self):
        """
        Each book card links to the detail route
        'book_detail' with the book pk.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_books_statuses()

        response = self.client.get(reverse("library"))

        u1 = reverse("book_detail", args=[self.book_to_read.pk])
        u2 = reverse("book_detail", args=[self.book_reading.pk])
        u3 = reverse("book_detail", args=[self.book_read.pk])

        self.assertContains(response, f'href="{u1}"')
        self.assertContains(response, f'href="{u2}"')
        self.assertContains(response, f'href="{u3}"')


class LibraryPageActionsTests(TestCase):
    """
    Tests that simulate how the Library page posts the hidden forms and
    renders the action links inside each row.
    """
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pw")
        self.book = Book.objects.create(
            id="TEST-BOOK-2", title="Another Book", authors=["B Two"]
        )
        self.client.login(username="u1", password="pw")

        self.next_url = (
            reverse("library")
            + "?status=ALL&sort=updated&dir=desc"
            )

    def test_remove_from_library_deletes_and_redirects(self):
        """ Remove from Library (library page)"""
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book,
            status="TO_READ"
            )

        url = reverse("set_reading_status", args=[self.book.id])
        resp = self.client.post(
            url,
            data={"status": "NONE", "next": self.next_url}
            )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith(reverse("library")))

        self.assertFalse(
            ReadingStatus.objects.filter(
                user=self.user,
                book=self.book
                ).exists()
        )
        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Removed your reading status.", msgs)

    def test_change_status_to_to_read_from_library(self):
        """ Change status to TO_READ from library"""
        # set different status so we assert the change
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book,
            status="READING"
            )

        url = reverse("set_reading_status", args=[self.book.id])
        resp = self.client.post(
            url,
            data={"status": "TO_READ", "next": self.next_url}
            )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith(reverse("library")))

        rs = ReadingStatus.objects.get(
            user=self.user,
            book=self.book
            )
        self.assertEqual(rs.status, "TO_READ")

        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Saved to your list.", msgs)

    def test_change_status_to_reading_from_library(self):
        """ Change status to READING from library"""
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book,
            status="TO_READ"
            )

        url = reverse("set_reading_status", args=[self.book.id])
        resp = self.client.post(
            url,
            data={"status": "READING", "next": self.next_url}
            )
        self.assertEqual(resp.status_code, 302)
        rs = ReadingStatus.objects.get(user=self.user, book=self.book)
        self.assertEqual(rs.status, "READING")

    def test_change_status_to_read_from_library(self):
        """ Change status to READ from library"""
        ReadingStatus.objects.create(
            user=self.user,
            book=self.book,
            status="TO_READ"
            )

        url = reverse("set_reading_status", args=[self.book.id])
        resp = self.client.post(
            url,
            data={"status": "READ", "next": self.next_url}
            )
        self.assertEqual(resp.status_code, 302)
        rs = ReadingStatus.objects.get(user=self.user, book=self.book)
        self.assertEqual(rs.status, "READ")

    def test_library_actions_render_review_and_rating_links(self):
        """
      Verify the Library HTML contains the correct hrefs for the rows actions:
          - Write a review -> book detail #reviews
          - Rate -> book detail
        """
        # Ensure the row exists (status presence isn't required but fine)
        ReadingStatus.objects.get_or_create(
            user=self.user, book=self.book, defaults={"status": "TO_READ"}
        )

        page = self.client.get(reverse("library"))
        self.assertEqual(page.status_code, 200)

        detail_url = reverse("book_detail", args=[self.book.id])
        self.assertContains(page, f'href="{detail_url}#reviews"')
        self.assertContains(page, f'href="{detail_url}')
