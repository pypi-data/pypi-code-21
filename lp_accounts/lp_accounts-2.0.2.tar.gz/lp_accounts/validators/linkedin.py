from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from .base import BaseValidator

import requests


class LinkedInValidator(BaseValidator):
    def __init__(self):
        self.valid = False
        if settings.LP_ACCOUNTS_LINKEDIN_APP_ID and settings.LP_ACCOUNTS_LINKEDIN_APP_SECRET:
            self.valid = True

    def validate(self, token):
        if not self.valid:
            raise ValidationError('LinkedIn Login Not Supported')

        if settings.TESTING:
            response = Response(status=status.HTTP_200_OK)
        else:
            headers = {
                'Authorization': 'Bearer %s' % token
            }
            response = requests.get(settings.LP_ACCOUNTS_LINKEDIN_VALIDATION_URL, headers=headers)

        return response.status_code is status.HTTP_200_OK
