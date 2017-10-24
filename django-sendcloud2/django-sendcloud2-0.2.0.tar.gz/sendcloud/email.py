# -*- encoding: utf8 -*-

# clone and modify from freeyoung@github.com/django-sendcloud

import email.utils as rfc822
import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
import pydash as _

class SendCloudAPIError(Exception):
    pass


class EmailBackend(BaseEmailBackend):
    """
    A Django Email backend that uses send cloud.
    """

    def __init__(self, fail_silently=False, *args, **kwargs):
        api_user, api_key = (kwargs.pop('api_user', None),
                             kwargs.pop('api_key', None))

        super(EmailBackend, self).__init__(fail_silently=fail_silently,
                                           *args, **kwargs)
        try:
            self._api_user = api_user or _.get(settings, 'SENDCLOUD.email.api_user')
            self._api_key = api_key or _.get(settings, 'SENDCLOUD.email.api_key')
        except AttributeError:
            if fail_silently:
                self._api_user, self._api_key = None, None
            else:
                raise
        self._api_url = 'https://api.sendcloud.net/apiv2/mail/send'

    @property
    def api_user(self):
        return self._api_user

    @property
    def api_key(self):
        return self._api_key

    @property
    def api_url(self):
        return self._api_url

    def open(self):
        pass

    def close(self):
        pass

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False

        from_email = sanitize_address(email_message.from_email,
                                      email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]

        params = {
            "apiUser": self.api_user,
            "apiKey": self.api_key,
            "to": ';'.join(recipients),
            "from": from_email,
            "subject": email_message.subject,
            "plain": email_message.body,
            "replyTo": email_message.reply_to,
            "respEmailId": "true",
        }

        # Required, as SendCloud will overly escape fromName.
        # e.g. Example.com <mail@example.com>
        #      fromName will be parsed as "\"Example.com\""
        from_name, _ = rfc822.parseaddr(from_email)

        if from_name:
            params['fromName'] = from_name

        try:
            r = requests.post(self.api_url, data=params)
            res = r.json()
        except Exception:
            if not self.fail_silently:
                raise
            return False

        if not res['result']:
            if not self.fail_silently:
                raise SendCloudAPIError(res['message'])
            return False

        return True

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of
        email messages sent.
        """
        if not email_messages:
            return

        num_sent = 0

        for message in email_messages:
            if self._send(message):
                num_sent += 1

        return num_sent


__author__ = ('shell', )
