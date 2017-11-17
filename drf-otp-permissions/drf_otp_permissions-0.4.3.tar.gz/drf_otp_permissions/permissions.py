"""
Provides a set of pluggable OTP permission policies.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import send_mail

from rest_framework.permissions import BasePermission

from .otp import validate_otp


class IsValidOneTimePassword(BasePermission):
    """
    Allows access only to request with valid OTP in its header.
    """

    def has_permission(self, request, view):
        if request.user:
            if getattr(settings, 'DRF_OTP_PERMISSIONS_ALLOW_STAFF', True) and request.user.is_staff:
                if request.method == 'GET':
                    return True
            if getattr(settings, 'DRF_OTP_PERMISSIONS_ALLOW_SUPERUSER', True) and request.user.is_superuser:
                return True

        if hasattr(view, 'get_otp_key_location'):
            key_location = view.get_otp_key_location()
        else:
            key_location = getattr(view, 'otp_key_location', None)

        otp = request.META.get('HTTP_X_OTP', None)
        if not otp:
            otp = request.META.get('HTTP_X-OTP', None)
        if not otp:
            return False

        data = request.data
        if not isinstance(data, dict):
            data = data.dict()

        if not validate_otp(otp, data, key_location):
            admin_email_list = []
            for name, email in settings.ADMINS:
                admin_email_list.append(email)

            send_mail(
                'Attempt with Invalid OTP',
                'Request with invalid OTP has occurred at %s.' % self.__class__.__name__,
                settings.EMAIL_HOST_USER,
                admin_email_list,
                fail_silently=True,
            )
            return False
        return True