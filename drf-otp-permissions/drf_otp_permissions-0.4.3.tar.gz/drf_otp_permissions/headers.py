"""
Add OTP to header
"""
from __future__ import unicode_literals

from .otp import create_otp


def add_otp(data, key_location, headers):
    otp = create_otp(data, key_location)
    headers['X_OTP'] = otp
    headers['X-OTP'] = otp

    return headers