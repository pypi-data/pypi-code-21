# -*- coding: utf-8 -*-

from django.test import TestCase
from smtplib import SMTPException
from apollo.lib import emails
import mock
import pdb


class TestSendEmail(TestCase):
    def setUp(self):
        patch_django_send_email = mock.patch('apollo.lib.emails.send_mail')
        self.mock_django_send_mail = patch_django_send_email.start()

        self.addCleanup(patch_django_send_email.stop)

    def test_calling_send_without_from_email_raises_exception(self):
        self.assertRaises(AttributeError, emails.send, None, ['something@something.com'], 'Apollo Test', 'test')

    def test_calling_send_without_to_email_raises_exception(self):
        self.assertRaises(AttributeError, emails.send, 'test@sender.com', None, 'Apollo Test', 'test')
        self.assertRaises(AttributeError, emails.send, 'test@sender.com', [], 'Apollo Test', 'test')

    def test_smtp_exception_sending_email_returns_false(self):
        self.mock_django_send_mail.side_effect = [SMTPException("error sending email")]

        self.assertFalse(emails.send(from_email='test@sender.com', to_emails=['test@receiver.com'], content='test'))

    def test_no_send_errors_returns_true(self):
        self.assertTrue(emails.send(from_email='test@sender.com', to_emails=['test@receiver.com'], content='test'))

    def test_proxies_django_send_mail(self):
        emails.send(from_email='test@sender.com', to_emails=['test@receiver.com'], subject='Apollo Test', content='test')

        self.assertIsNone(
            self.mock_django_send_mail.assert_called_with(
                'Apollo Test',
                'test',
                'test@sender.com',
                ['test@receiver.com'],
                fail_silently=False
            )
        )

    def test_handles_spanish_characters(self):
        span_chars = "años luz detrás"
        emails.send(from_email='test@sender.com', to_emails=['test@receiver.com'], subject='Apollo Test', content=span_chars)