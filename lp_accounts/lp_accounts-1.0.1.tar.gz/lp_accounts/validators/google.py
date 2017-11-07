from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from .base import BaseValidator

import requests


class GoogleValidator(BaseValidator):
    def __init__(self):
        self.valid = False
        if settings.LP_ACCOUNTS_GOOGLE_APP_ID:
            self.valid = True

    def validate(self, token):
        if not self.valid:
            raise ValidationError('Google Sign-In Not Supported')

        if settings.TESTING:
            response = Response(status=status.HTTP_200_OK)
        else:
            response = requests.get(settings.LP_ACCOUNTS_GOOGLE_VALIDATION_URL % token)

        return response.status_code is status.HTTP_200_OK
