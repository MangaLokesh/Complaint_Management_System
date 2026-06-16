import importlib
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient


class EmailConfigTests(SimpleTestCase):
    def test_uses_console_backend_when_smtp_credentials_are_missing(self):
        with mock.patch.dict('os.environ', {}, clear=True):
            import cmsproject.settings as settings_module

            reloaded = importlib.reload(settings_module)

            self.assertEqual(
                reloaded.EMAIL_BACKEND,
                'django.core.mail.backends.console.EmailBackend',
            )


class SmsResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='smsuser',
            email='sms@example.com',
            password='secret123',
        )
        self.user.profile = None

    def test_sms_reset_endpoint_returns_success(self):
        self.user.profile = None
        self.user.save()
        from users.models import UserProfile

        UserProfile.objects.create(user=self.user, phone_number='+15551234567')

        with mock.patch('users.views._send_sms_message', return_value=True) as send_sms:
            response = self.client.post('/api/password-reset/sms/', {'phone_number': '+15551234567'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(send_sms.called)
        self.assertIn('Password reset link sent via SMS', response.json()['message'])
