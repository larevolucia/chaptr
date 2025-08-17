# tests/tests_allauth.py
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ACCOUNT_EMAIL_VERIFICATION="mandatory",        # <-- force confirmation email
    ACCOUNT_EMAIL_REQUIRED=True,                   # <-- make email required
    ACCOUNT_AUTHENTICATION_METHOD="username_email",
    SITE_ID=1,
)
class SignupBasicsTests(TestCase):

    def test_signup_page_renders(self):
        url = reverse("account_signup")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="username"', html=False)
        self.assertContains(resp, 'name="email"', html=False)
        self.assertContains(resp, 'name="password1"', html=False)
        self.assertContains(resp, 'name="password2"', html=False)

    def test_signup_success_shows_feedback_and_sends_confirmation(self):
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
        self.assertGreaterEqual(len(mail.outbox), 1, f"Outbox empty. Settings in test may not be applied. Current outbox: {mail.outbox}")
