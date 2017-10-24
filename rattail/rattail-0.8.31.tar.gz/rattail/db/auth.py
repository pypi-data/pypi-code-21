# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Authentication & Authorization
"""

from __future__ import unicode_literals, absolute_import

import bcrypt
import six

from rattail.db import model


def authenticate_user(session, username, password):
    """
    Attempt to authenticate a user.

    :returns: A :class:`.model.User` instance, if successful.  Otherwise
       returns ``None``.
    """
    user = session.query(model.User)\
        .filter_by(username=username)\
        .first()
    if user and user.active and user.password is not None:
        # apparently bcrypt's hashpw() doesn't like Unicode
        if isinstance(password, six.text_type):
            password = password.encode('utf_8')
        salt = user.salt.encode('utf_8')
        try:
            authenticated = (bcrypt.hashpw(password, salt) == user.password)
        except UnicodeEncodeError:
            authenticated = False
        if authenticated:
            return user
    return None


def set_user_password(user, password):
    """
    Set a user's password.
    """
    # apparently bcrypt's hashpw() doesn't like Unicode
    if isinstance(password, six.text_type):
        password = password.encode('utf_8')
    user.salt = bcrypt.gensalt()
    user.password = bcrypt.hashpw(password, user.salt)


def special_role(session, uuid, name):
    """
    Fetches, or creates, a "special" role.
    """

    role = session.query(model.Role).get(uuid)
    if not role:
        role = model.Role(uuid=uuid, name=name)
        session.add(role)
    return role


def administrator_role(session):
    """
    Returns the "Administrator" role.
    """

    return special_role(session, 'd937fa8a965611dfa0dd001143047286', 'Administrator')


def guest_role(session):
    """
    Returns the "Guest" role.
    """

    return special_role(session, 'f8a27c98965a11dfaff7001143047286', 'Guest')


def authenticated_role(session):
    """
    Returns the "Authenticated" role.
    """
    return special_role(session, 'b765a9cc331a11e6ac2a3ca9f40bc550', "Authenticated")


def grant_permission(role, permission):
    """
    Grant a permission to a role.
    """

    # TODO: Make this a `Role` method (or make `Role.permissions` a `set` so we
    # can do `role.permissions.add('some.perm')` ?).
    if permission not in role.permissions:
        role.permissions.append(permission)


def has_permission(session, principal, permission, include_guest=True, include_authenticated=True):
    """
    Determine if a principal has been granted a permission.

    :param session: A SQLAlchemy session instance.

    :param principal: May be either a :class:`.model.User` or
       :class:`.model.Role` instance.  It is also expected that this may
       sometimes be ``None``, in which case the "Guest" role will typically be
       assumed.

    :param permission: The full internal name of a permission,
       e.g. ``'users.create'``.

    :param include_guest: Whether or not the "Guest" role should be included
       when checking permissions.  If ``False``, then Guest's permissions will
       *not* be consulted.

    :param include_authenticated: Whether or not the "Authenticated" role
       should be included when checking permissions.

    Note that if no ``principal`` is provided, and ``include_guest`` is set to
    ``False``, then no checks will actually be done, and the return value will
    be ``False``.
    """

    if hasattr(principal, 'roles'):
        roles = list(principal.roles)
        if include_authenticated:
            roles.append(authenticated_role(session))
    elif principal is not None:
        roles = [principal]
    else:
        roles = []

    if include_guest:
        roles.append(guest_role(session))
    for role in roles:
        for perm in role.permissions:
            if perm == permission:
                return True
    return False
