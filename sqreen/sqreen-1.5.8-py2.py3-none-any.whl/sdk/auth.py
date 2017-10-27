# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Authentication sdk functions
"""


def auth_track(success, **user_identifiers):
    """ Register a successfull or failed authentication attempt (based on
    success boolean) for an user identified by the keyword-arguments.
    For example:

    auth_track(True, email="foobar@example.com") register a successfull
    authentication attempt for user with email "foobar@example.com".

    auth_track(False, user_id=42) register a failed authentication
    attempt for user with id 42.
    """
    pass


def signup_track(**user_identifiers):
    """ Register a new account signup identified by the keyword-arguments.
    For example:

    auth_track(email="foobar@example.com", user_id=42) register
    a new account signup for user identifed by email "foobar@example.com" or
    bu user id 42.
    """
    pass
