import itertools

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

import falcon
from falcon_helpers.sqla.orm import BaseColumns, metadata, ModelBase

from wrapt import decorator


user_groups = sa.Table('auth_user_groups', metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('auth_users.id')),
    sa.Column('group_id', sa.Integer, sa.ForeignKey('auth_groups.id'))
)

user_permissions = sa.Table('auth_user_permissions', metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('auth_users.id')),
    sa.Column('permissions_id', sa.Integer, sa.ForeignKey('auth_permissions.id'))
)

group_permissions = sa.Table('auth_group_permissions', metadata,
    sa.Column('group_id', sa.Integer, sa.ForeignKey('auth_groups.id')),
    sa.Column('permissions_id', sa.Integer, sa.ForeignKey('auth_permissions.id'))
)


class User(ModelBase, BaseColumns):
    __tablename__ = 'auth_users'

    ident = sa.Column(sa.Unicode, nullable=False, unique=True)


    def __repr__(self):
        return self.ident

    def __str__(self):
        return self.ident

    @classmethod
    def get_by_id(cls, ident):
        return sa.orm.Query(cls).filter(cls.ident == ident)

    @declared_attr
    def groups(cls):
        return sa.orm.relationship('Group', secondary='auth_user_groups')

    @declared_attr
    def assigned_permissions(cls):
        return sa.orm.relationship('Permission', secondary='auth_user_permissions')

    @property
    def permissions(self):
        group_perms = list(itertools.chain.from_iterable(
            [x.permissions for x in self.groups]))
        user_perms = self.assigned_permissions
        return list(itertools.chain(user_perms, group_perms))

    def has_permission(self, token):
        if not token:
            return False

        if not isinstance(token, str):
            raise ValueError('Token must be a string when using has_permission')

        return token in self.permissions


class Group(ModelBase, BaseColumns):
    __tablename__ = 'auth_groups'

    ident = sa.Column(sa.Unicode, nullable=False, unique=True)

    def __repr__(self):
        return self.ident

    def __str__(self):
        return self.ident

    @declared_attr
    def permissions(cls):
        return sa.orm.relationship('Permission', secondary='auth_group_permissions')


class Permission(ModelBase, BaseColumns):
    __tablename__ = 'auth_permissions'

    ident = sa.Column(sa.Unicode, nullable=False, unique=True)

    def __repr__(self):
        return self.ident

    def __str__(self):
        return self.ident

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.ident

        else:
            super().__eq__(other)


def raise_unauthenticated(*args, **kwargs):
    raise falcon.HTTPUnauthorized()


def route_requires_permission(token=None, on_fail=raise_unauthenticated):
    """Decorate a route to require a certain permission

    This should be used on a falcon resource method such as `on_get`, `on_post`
    to require a base permission for the route. Omitting the token permission
    token requires that the user exists to access that route.

    :param token: the permision token to require
    :param on_fail: a function to execute when the permission check fails.

    NOTE: By default this function will raise an HTTPUnauthorized exception
    """

    @decorator
    def wrapper(wrapped, instance, args, kwargs):
        if (args[0] and
            args[0].context and
            args[0].context.get('user') and
            args[0].context.get('user').has_permission(token)):

            return wrapped(*args, **kwargs)
        else:
            return on_fail(*args, **kwargs)

    return wrapper


def has_permission(user, token):
    return (user and user.has_permission(token))


def has_any_permission(user, tokens):
    return (user and any([user.has_permission(x) for x in tokens]))


def has_all_permissions(user, tokens):
    return (user and all([user.has_permission(x) for x in tokens]))
