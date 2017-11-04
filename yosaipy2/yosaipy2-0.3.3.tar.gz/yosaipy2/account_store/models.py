#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseModelImpl(object):
    def __init__(self, pk_id, name):
        self.pk_id = pk_id
        self.name = name

    @classmethod
    def table(cls):
        return cls.__name__

    def __repr__(self):
        return "{}.{}".format(self.pk_id, self.name)


class Resource(BaseModelImpl):
    pass


class Action(BaseModelImpl):
    pass


class Domain(BaseModelImpl):
    pass


class CredentialType(BaseModelImpl):
    pass


class Role(BaseModelImpl):
    def __init__(self, pk_id, name, permission_ids):
        super(Role, self).__init__(pk_id, name)
        self._permission_ids = permission_ids

    @property
    def permission_ids(self):
        return self._permission_ids


class User(BaseModelImpl):
    def __init__(self, pk_id, name, **kwargs):
        super(User, self).__init__(pk_id, name)
        self._profile = kwargs

    @property
    def identifier(self):
        """
        identifier of this user
        :return:
        """
        return self.pk_id

    @property
    def account_lock_millis(self):
        """
        locked milliseconds of this user
        :return:
        """
        if 'account_lock_millis' in self._profile:
            return self._profile['account_lock_millis']
        else:
            return 0

    @property
    def phone_number(self):
        """
        phone number of this user
        :return:
        """
        if 'phone_number' in self._profile:
            return self._profile['phone_number']
        else:
            return ''

    @property
    def role_ids(self):
        """
        roles associated with this user
        :return:
        """
        if 'role_ids' in self._profile:
            return self._profile['role_ids']
        else:
            return []


class Permission(BaseModelImpl):
    def __init__(self, pk_id, name, **kwargs):
        super(Permission, self).__init__(pk_id, name)
        self._profile = kwargs

    @property
    def domain(self):
        """
        domain of the permission
        :return:
        """
        if 'domain' in self._profile:
            return self._profile['domain']
        else:
            return ''

    @property
    def actions(self):
        """
        actions associated with this permission
        :return:
        """
        if 'actions' in self._profile:
            return self._profile['actions']
        else:
            return ''

    @property
    def resources(self):
        """
        resources associated with this permission
        :return:
        """
        if 'resources' in self._profile:
            return self._profile['resources']
        else:
            return ''

    @property
    def roles(self):
        """
        roles associated with this permission
        :return:
        """
        if 'roles' in self._profile:
            return self._profile['roles']
        else:
            return ''

    @roles.setter
    def roles(self, v):
        self._profile['roles'] = v

    @property
    def users(self):
        """
        users associated with this permission
        :return:
        """
        if 'users' in self._profile:
            return self._profile['users']
        else:
            return ''

    @users.setter
    def users(self, v):
        self._profile['users'] = v


class Credential(BaseModelImpl):
    def __init__(self, pk_id, name, **kwargs):
        super(Credential, self).__init__(pk_id, name)
        self._profile = kwargs

    @property
    def user_id(self):
        """
        user_id associated with this Credential
        :return:
        """
        if 'user_id' in self._profile:
            return self._profile['user_id']
        else:
            return ''

    @property
    def credential(self):
        """
        credential associated with this Credential
        :return:
        """
        if 'credential' in self._profile:
            return self._profile['credential']
        else:
            return ''

    @property
    def credential_type(self):
        """
        credential type associated with this Credential
        :return:
        """
        if 'credential_type' in self._profile:
            return self._profile['credential_type']
        else:
            return ''

    @property
    def expiration_dt(self):
        """
        expiration_dt associated with this Credential
        :return:
        """
        if 'expiration_dt' in self._profile:
            return self._profile['expiration_dt']
        else:
            return ''

    @property
    def user(self):
        """
        user associated with this permission
        :return:
        """
        if 'user' in self._profile:
            return self._profile['user']
        else:
            return ''

    @user.setter
    def user(self, v):
        """
        :return:
        """
        self._profile['user'] = v
