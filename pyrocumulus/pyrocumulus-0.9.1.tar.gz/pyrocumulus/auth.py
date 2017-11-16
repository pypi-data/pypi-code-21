# -*- coding: utf-8 -*-

# Copyright 2015 Juca Crispim <juca@poraodojuca.net>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus. If not, see <http://www.gnu.org/licenses/>.


import uuid
from tornado import gen
from mongomotor import Document
from mongomotor.fields import ReferenceField, StringField, ListField
from pyrocumulus.utils import bcrypt_string, fqualname


# Models for basic auth
class AccessToken(Document):
    name = StringField()
    token = StringField(required=True)
    domains = ListField(StringField())

    def generate_token(self):
        token = str(uuid.uuid4())
        return token

    @classmethod
    @gen.coroutine
    def get_by_token(cls, token):
        bcrypt_token = bcrypt_string(token)
        access_token = yield cls.objects.get(token=bcrypt_token)
        return access_token

    @gen.coroutine
    def save(self):
        if not self.token:
            token = self.generate_token()
            self.token = bcrypt_string(token)
        yield super().save()
        return token

    @gen.coroutine
    def get_perms(self, model):
        """ Returns the permissions for this token on a given model.
        :param model: mongomotor.Document instance or fqualname
        """

        if not isinstance(model, str):
            model = fqualname(model)

        perms = Permission.objects.filter(access_token=self, model=model)
        perms_list = []
        for perm in (yield perms.to_list()):
            perms_list += list(perm.perms)

        perms = set(perms_list)
        return perms

    @gen.coroutine
    def has_create_perm(self, model):
        perms = yield self.get_perms(model)
        return 'c' in perms

    @gen.coroutine
    def has_retrieve_perm(self, model):
        perms = yield self.get_perms(model)
        return 'r' in perms

    @gen.coroutine
    def has_update_perm(self, model):
        perms = yield self.get_perms(model)
        return 'u'in perms

    @gen.coroutine
    def has_delete_perm(self, model):
        perms = yield self.get_perms(model)
        return 'd' in perms


class Permission(Document):
    access_token = ReferenceField(AccessToken, required=True)
    # model is pyrocumulus.utils.fqualname(ModelClass)
    model = StringField(required=True)
    # perms are 'r' for retrieve, 'c' for create, 'u' for update
    # and 'd' for delete. The perms string can be any combination of these
    # 4 letters.
    perms = StringField(required=True)

    @classmethod
    @gen.coroutine
    def create_perms_to(cls, access_token, model, perms):
        """ Creates a Permission instance to ``token`` related to ``model``.
        :param access_token: AccessToken instance
        :param model: class or fqualname
        :param perms: perms to apply ('r', 'c', 'u', 'd')
        """

        if not isinstance(model, str):
            model = fqualname(model)

        perms = cls(access_token=access_token, model=model, perms=perms)
        yield perms.save()
        return perms
