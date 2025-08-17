"""Tests for allauth implementation.

Covers:
- Sign-up form rendering.


"""
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")  # noqa: E501
class SignupBasicsTests(TestCase):
    """Tests for the signup process."""
    def test_signup_page_renders(self):
        """Test that the signup page renders correctly."""
        url = reverse("account_signup")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # form fields present (username, email, password1/2)
        self.assertContains(resp, "name=\"username\"", html=False)
        self.assertContains(resp, "name=\"email\"", html=False)
        self.assertContains(resp, "name=\"password1\"", html=False)
        self.assertContains(resp, "name=\"password2\"", html=False)
