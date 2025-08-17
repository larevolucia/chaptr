"""
    Tests for the signup process using allauth.

    Covers:
    - Rendering of the signup page
    - Successful signup process
    - Validation errors during signup
"""
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model


User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ACCOUNT_EMAIL_VERIFICATION="mandatory",
    ACCOUNT_EMAIL_REQUIRED=True,
    ACCOUNT_AUTHENTICATION_METHOD="username_email",
    SITE_ID=1,
)
class SignupBasicsTests(TestCase):
    """Tests for the signup process using allauth."""
    def test_signup_page_renders(self):
        """Test that the signup page renders correctly."""
        url = reverse("account_signup")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="username"', html=False)
        self.assertContains(resp, 'name="email"', html=False)
        self.assertContains(resp, 'name="password1"', html=False)
        self.assertContains(resp, 'name="password2"', html=False)

    def test_signup_success_shows_feedback_and_sends_confirmation(self):
        """
            Test that a successful signup shows feedback
            and sends a confirmation email.
        """
        signup_url = reverse("account_signup")
        data = {
            "username": "reader1",
            "email": "reader1@example.com",
            "password1": "S3curepass!123",
            "password2": "S3curepass!123",
        }
        resp = self.client.post(signup_url, data, follow=True)

        # With mandatory verification: user is NOT logged in yet
        self.assertFalse(resp.context["user"].is_authenticated)

        # A confirmation email MUST be sent
        self.assertGreaterEqual(len(mail.outbox), 1, f"Outbox empty. Settings in test may not be applied. Current outbox: {mail.outbox}")  # noqa: E501 pylint: disable=line-too-long

    def test_signup_validation_errors(self):
        """Test that signup shows validation errors."""
        # follow redirects so we land on a page with a form in context
        User.objects.create_user(
            username="reader2", email="reader2@example.com", password="Xx12345678!"  # noqa: E501 pylint: disable=line-too-long
        )
        signup_url = reverse("account_signup")
        bad_data = {
            "username": "reader2",                 # already taken
            "email": "reader2@example.com",        # already taken
            "password1": "short",                  # too short
            "password2": "different",              # mismatch (no output)
        }
        resp = self.client.post(signup_url, bad_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid signup")  # noqa: E501 pylint: disable=line-too-long

        self.assertIn("username", form.errors)
        self.assertIn("password1", form.errors)

        self.assertContains(resp, "This password is too short. It must contain at least 8 characters.", status_code=200)  # noqa: E501 pylint: disable=line-too-long
        self.assertContains(resp, "A user with that username already exists.", status_code=200)  # noqa: E501 pylint: disable=line-too-long


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ACCOUNT_EMAIL_VERIFICATION="mandatory",
    ACCOUNT_EMAIL_REQUIRED=True,
    ACCOUNT_AUTHENTICATION_METHOD="username",
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True,
    SITE_ID=1,
)
class LoginLogoutTests(TestCase):
    """Tests for the login and logout process using allauth."""

    def setUp(self):
        """Create a test user and e-mail for login tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="S3curepass!123"
        )
        self.user.emailaddress_set.create(
            email="testuser@example.com",
            verified=True,
            primary=True
        )

    def test_login_page_renders(self):
        """Test that the login page renders correctly."""
        url = reverse("account_login")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="login"', html=False)
        self.assertContains(resp, 'name="password"', html=False)
        self.assertContains(resp, "Log In", html=False)

    def test_successful_login_with_username(self):
        """Test successful login using username."""
        login_url = reverse("account_login")
        data = {
            "login": "testuser",
            "password": "S3curepass!123",
        }
        resp = self.client.post(login_url, data, follow=True)

        self.assertTrue(resp.context["user"].is_authenticated)
        self.assertEqual(resp.context["user"].username, "testuser")

        self.assertRedirects(resp, "/")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ACCOUNT_EMAIL_VERIFICATION="none",
    ACCOUNT_EMAIL_REQUIRED=True,
    ACCOUNT_AUTHENTICATION_METHOD="username",
    SITE_ID=1,
)
class PasswordResetTests(TestCase):
    """Test password reset functionality."""

    def setUp(self):
        """Create a test user with email for password reset tests."""
        self.user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="OldPassword123!"
        )

    def test_password_reset_page_renders(self):
        """Test that the password reset page renders correctly."""
        url = reverse("account_reset_password")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Password Reset", html=False)
        self.assertContains(resp, 'name="email"', html=False)
        self.assertContains(resp, "Reset My Password", html=False)
