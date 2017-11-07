# -*- coding: utf-8 -*-


def user_has_privilege(user, privilege):
    if not hasattr(user, 'extra'):
        return False

    privilege_list = [priv.strip() for priv in user.extra.remote_privileges.split('|')]
    return privilege in privilege_list
