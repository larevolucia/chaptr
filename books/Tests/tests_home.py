"""Tests for the home page view and template."""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeViewTests(TestCase):
    """Tests for the home page view and template."""
    def setUp(self):
        # Create a test user for authentication tests.
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="S3curepass!123"
        )

    def test_home_view_renders(self):
        """Test that the home page loads without errors."""
        url = reverse("home")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that home view uses the correct template."""
        url = reverse("home")
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'books/home.html')

    def test_home_page_extends_base_template(self):
        """Test that essential base template elements are present."""
        url = reverse("home")
        resp = self.client.get(url)

        # Check for base template elements
        self.assertContains(resp, 'data-testid="header"', html=False)
        self.assertContains(resp, 'data-testid="footer"', html=False)
        self.assertContains(resp, 'data-testid="skip-to-main"', html=False)

    def test_search_form_inclusion(self):
        """Test that the search form is included in the header."""
        url = reverse("home")
        resp = self.client.get(url)

        # Check for search form elements based on search_form.html
        self.assertContains(resp, 'id="search-q"', html=False)
        self.assertContains(resp, 'id="search-field"', html=False)
        self.assertContains(resp, 'role="search"', html=False)
        self.assertContains(resp, 'data-testid="search-form"', html=False)

        # Check for specific form action
        self.assertContains(resp, 'action="/search/"', html=False)

        # Check dropdown options
        self.assertContains(
            resp,
            '<option value="all">All</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="title">Title</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="author">Author</option>',
            html=False
            )
        self.assertContains(
            resp,
            '<option value="subject">Genre</option>',
            html=False
            )

    def test_anonymous_user_sees_auth_links(self):
        """Test that anonymous users see sign up and log in links."""
        url = reverse("home")
        resp = self.client.get(url)

        self.assertContains(resp, 'data-testid="sign-up"', html=False)
        self.assertContains(resp, 'data-testid="log-in"', html=False)

        self.assertContains(resp, reverse("account_signup"), html=False)
        self.assertContains(resp, reverse("account_login"), html=False)

    def test_authenticated_user_sees_welcome_and_menu(self):
        """Test that logged-in users see welcome message and account menu."""
        self.client.force_login(self.user)

        url = reverse("home")
        resp = self.client.get(url)

        self.assertContains(resp, 'id="account-welcome"', html=False)

        self.assertContains(resp, 'aria-label="Account menu"', html=False)
        self.assertContains(resp, reverse("account_logout"), html=False)

        self.assertNotContains(resp, 'data-testid="sign-up"', html=False)
        self.assertNotContains(resp, 'data-testid="log-in"', html=False)

    def test_hero_section_content(self):
        """Test that hero section contains expected content."""
        url = reverse("home")
        resp = self.client.get(url)

        # Hero title and description
        self.assertContains(resp, 'data-testid="hero-container"', html=False)
        self.assertContains(resp, 'data-testid="hero-title"', html=False)
        self.assertContains(resp, 'data-testid="hero-text"', html=False)

    def test_about_section_content(self):
        """Test that the about section renders correctly."""
        url = reverse("home")
        resp = self.client.get(url)

        self.assertContains(resp, 'data-testid="about-section"', html=False)

    def test_genre_section_content(self):
        """Test that genre browsing section renders correctly."""
        url = reverse("home")
        resp = self.client.get(url)

        # Genre section header
        self.assertContains(resp, "Browse by Genre", html=False)

        # Individual genre cards
        self.assertContains(resp, "Sci-Fi", html=False)
        self.assertContains(resp, "Mystery", html=False)
        self.assertContains(resp, "Non-Fiction", html=False)

        # Genre links
        self.assertContains(
            resp,
            "/search/?field=subject&q=science%20fiction",
            html=False
            )
        self.assertContains(
            resp,
            "/search/?field=subject&q=mystery",
            html=False
            )
        self.assertContains(
            resp,
            "/search/?field=subject&q=nonfiction",
            html=False
            )
