# BOTLIB Framework to program bots
#
# botlib/users.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" class to access user records. """

from .defines import permissions, exclusive
from .db import Db
from .object import Object
from .utils import stripped

import logging

class User(Object):

    """ User object to store user data. """

    pass

class Users(Db):

    """ Users class providing methods to check/verify/allow users based on origin. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._origins = Object()

    def allowed(self, origin, perm):
        """ check whether a user has a permission. """
        from .space import cfg, fleet
        perm = perm.upper()
        user = self.fetch(origin)
        if user and perm in user.perms:
            return True
        logging.warn("# denied %s %s" % (origin, perm))
        return False

    def delete(self, origin, perm):
        """ add a user to the store. """
        user = self.fetch(origin)
        if user:
            try:
                user.perms.remove(perm)
                user.sync()
            except ValueError:
                pass
        return user

    def fetch(self, origin):
        """ return user data. """
        if origin in self._origins:
            return self._origins[origin]
        user = self.last("user", origin)
        if not user:
            user = self.last("user", stripped(origin))
        if user:
            self._origins[origin] = user
        return user

    def meet(self, origin):
        """ add a user to the store. """
        logging.warn("# meet %s" % origin)
        user = self.fetch(origin)
        if not user:
            user = User()
            user.user = origin
            user.origin = origin
            user.perms = ["USER",]
            user.save()
        return user

    def oper(self, origin):
        """ add a user to the store. """
        logging.info("# oper %s" % origin)
        opers = self.fetch(origin)
        if not opers:
            user = User()
            user.user = origin
            user.perms = permissions
            user.save()
            return user

    def uber(self, origin):
        """ add a user to the store. """
        logging.info("# uber %s" % origin)
        opers = self.fetch(origin)
        if not opers:
            user = User()
            user.user = origin
            user.perms = permissions + exclusive
            user.save()
            return user

    def perm(self, origin, perm):
        """ set a permission of a user. """
        logging.warn("# perm %s %s" % (origin, perm))
        user = self.fetch(origin)
        if user:
            if perm.upper() not in user.perms:
                user.perms.append(perm.upper())
                user.sync()
        return user
