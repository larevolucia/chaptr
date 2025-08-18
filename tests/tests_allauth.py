"""
    Tests for the signup process using allauth.

    Covers:
    - Rendering of the signup page
    - Successful signup process
    - Validation errors during signup
    - Username and password validation errors
    - Reset password page and e-mail trigger
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

    def test_signup_username_taken(self):
        """
        Test that signup shows validation error
        for taken username.
        """
        User.objects.create_user(
            username="reader2", email="reader2@example.com", password="Xx12345678!"  # noqa: E501 pylint: disable=line-too-long
        )
        signup_url = reverse("account_signup")
        bad_data = {
            "username": "reader2",                 # already taken
            "email": "reader2@example.com",        # already taken
            "password1": "T3stPassword!",
            "password2": "T3stPassword!",
        }
        resp = self.client.post(signup_url, bad_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid signup")  # noqa: E501 pylint: disable=line-too-long

        self.assertIn("username", form.errors)

        self.assertContains(resp, "A user with that username already exists.", status_code=200)  # noqa: E501 pylint: disable=line-too-long

    def test_signup_password_too_short(self):
        """
        Test that signup shows validation error
        for password too short.
        """
        # follow redirects so we land on a page with a form in context
        User.objects.create_user(
            username="reader1", email="reader1@example.com", password="Xx12345678!"  # noqa: E501 pylint: disable=line-too-long
        )
        signup_url = reverse("account_signup")
        bad_data = {
            "username": "reader2",
            "email": "reader2@example.com",
            "password1": "short",                  # too short
            "password2": "short",
        }
        resp = self.client.post(signup_url, bad_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid signup")  # noqa: E501 pylint: disable=line-too-long

        self.assertIn("password1", form.errors)

        self.assertContains(resp, "This password is too short. It must contain at least 8 characters.", status_code=200)  # noqa: E501 pylint: disable=line-too-long

    def test_signup_password_mismatch(self):
        """
        Test that signup shows validation error
        for password mismatch.
        """
        signup_url = reverse("account_signup")
        bad_data = {
            "username": "reader",
            "email": "reader@example.com",
            "password1": "P@ssW0rd1!",
            "password2": "P@ssW0rd1!different",  # mismatch
        }
        resp = self.client.post(signup_url, bad_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid signup")  # noqa: E501 pylint: disable=line-too-long

        self.assertIn("password2", form.errors)

        self.assertContains(resp, "You must type the same password each time.", status_code=200)  # noqa: E501 pylint: disable=line-too-long


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

    def test_login_empty_username_validation(self):
        """Test login form username validation error."""
        login_url = reverse("account_login")
        data = {
            "login": "",  # Empty username
            "password": "Password!123",  # Valid password
        }
        resp = self.client.post(login_url, data, follow=True)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid login")  # noqa: E501 pylint: disable=line-too-long

        # Check that form has errors
        self.assertTrue(form.errors)
        self.assertIn("login", form.errors)

    def test_login_empty_password_validation(self):
        """Test login form password validation error."""
        login_url = reverse("account_login")
        data = {
            "login": "testuser",
            "password": "",  # Empty password
        }
        resp = self.client.post(login_url, data, follow=True)

        form = resp.context.get("form")
        self.assertIsNotNone(form, "Expected 'form' in template context after invalid login")  # noqa: E501 pylint: disable=line-too-long

        # Check that form has errors
        self.assertTrue(form.errors)
        self.assertIn("password", form.errors)

    def test_login_with_nonexistent_user_fails(self):
        """Authentication should fail with a non-existent username."""
        login_url = reverse("account_login")
        data = {
            "login": "reader2",  # Non-existent username
            "password": "Password!123",
        }
        resp = self.client.post(login_url, data, follow=True)

        form = resp.context.get("form")
        self.assertTrue(
            any("username" in e.lower() or "password" in e.lower() for e in form.errors["__all__"]),  # noqa: E501 pylint: disable=line-too-long
            f"Expected a generic auth error, got: {form.errors}"
            )

        self.assertContains(resp, "The username and/or password you specified are not correct.", status_code=200)  # noqa: E501 pylint: disable=line-too-long

    def test_login_with_invalid_password_fails(self):
        """Test that login fails with an invalid password."""
        User.objects.create_user(
            username="reader2", email="reader2@example.com", password="Xx12345678!"  # noqa: E501 pylint: disable=line-too-long
        )
        login_url = reverse("account_login")
        data = {
            "login": "reader2",
            "password": "NOTXx12345678!",  # Invalid password
        }
        resp = self.client.post(login_url, data, follow=True)

        form = resp.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

        self.assertIn("__all__", form.errors)
        self.assertTrue(
            any("username" in e.lower() or "password" in e.lower() for e in form.errors["__all__"]),  # noqa: E501 pylint: disable=line-too-long
            f"Expected a generic auth error, got: {form.errors}"
        )


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

    def test_password_reset_sends_email(self):
        """Test that password reset sends an email."""
        # Clear any existing emails
        mail.outbox = []

        reset_url = reverse("account_reset_password")
        data = {
            "email": "resetuser@example.com",
        }
        resp = self.client.post(reset_url, data, follow=True)

        # Should redirect to password reset done page
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "We have sent you an email", html=False)

        # Should send exactly one email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["resetuser@example.com"])
        self.assertIn("password", email.subject.lower())
