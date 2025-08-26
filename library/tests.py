from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your tests here.

from books.models import Book
from activity.models import ReadingStatus


class LibraryViewTests(TestCase):
    """ Test the library views """
    def setUp(self):
        # Create a user we can log in with
        User = get_user_model()
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass1234"
        )
        self.book_to_read = Book.objects.create(id="to-read", title="To Read Book")
        self.book_reading = Book.objects.create(id="reading", title="Reading Book")
        self.book_read = Book.objects.create(id="read", title="Read Book")

    def set_book_to_read(self):
        """ Log a book with 'to read' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user, book=self.book_to_read, status=ReadingStatus.Status.TO_READ
        )

    def set_book_reading(self):
        """ Log a book with 'reading' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user, book=self.book_reading, status=ReadingStatus.Status.READING
        )

    def set_book_read(self):
        """ Log a book with 'read' status for the user."""
        self.client.login(username="alice", password="pass1234")
        ReadingStatus.objects.create(
            user=self.user, book=self.book_read, status=ReadingStatus.Status.READ
        )

    def set_books_statuses(self):
        """ Log three books with different statuses for the user."""
        self.client.login(username="alice", password="pass1234")
        self.set_book_to_read()
        self.set_book_reading()
        self.set_book_read()

    def test_navbar_links_visible_only_when_authenticated(self):
        """
        Navbar (in base.html) shows user dropdown items only for logged-in users.
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
        self.assertContains(response, "No books found in your library.")
        self.assertNotContains(response, ' id="to-read-collection"')
        self.assertNotContains(response, ' id="reading-collection"')
        self.assertNotContains(response, ' id="read-collection"')

    def test_library_page_with_books(self):
        """
        If the user has books in their library, they should see them organized by status.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_books_statuses()

        response = self.client.get(reverse("library"))
        self.assertContains(response, ' id="to-read-collection"')
        self.assertContains(response, ' id="reading-collection"')
        self.assertContains(response, ' id="read-collection"')

    def test_library_page_with_only_to_read_book(self):
        """
        If the user has only books on their to-read list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_to_read()

        response = self.client.get(reverse("library"))
        self.assertContains(response, ' id="to-read-collection"')
        self.assertNotContains(response, ' id="reading-collection"')

    def test_library_page_with_only_reading_book(self):
        """
        If the user has only books on their reading list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_reading()

        response = self.client.get(reverse("library"))
        self.assertNotContains(response, ' id="to-read-collection"')
        self.assertContains(response, ' id="reading-collection"')
        self.assertNotContains(response, ' id="read-collection"')

    def test_library_page_with_only_read_book(self):
        """
        If the user has only books on their reading list,
        they shouldn't see other collection headers.
        """
        self.client.login(username="alice", password="pass1234")

        self.set_book_read()

        response = self.client.get(reverse("library"))
        self.assertNotContains(response, ' id="to-read-collection"')
        self.assertNotContains(response, ' id="reading-collection"')
        self.assertContains(response, ' id="read-collection"')

    def test_each_book_links_to_its_detail_page(self):
        """
        Each book card links to the detail route 'book_detail' with the book pk.
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