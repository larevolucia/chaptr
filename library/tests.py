from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your tests here.

# from books.models import Book
# from activity.models import ReadingStatus


class LibraryViewTests(TestCase):
    """ Test the library views """
    def setUp(self):
        # Create a user we can log in with
        User = get_user_model()
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass1234"
        )

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
