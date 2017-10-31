
import json

ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class PermissionController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.permission import Permission
        from porper.models.user_group import UserGroup
        self.permission = Permission(connection)
        self.user_group = UserGroup(connection)
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(connection)

    def is_admin(self, user_id):
        row = self.user_group.find({'user_id': user_id, 'group_id': ADMIN_GROUP_ID})
        if len(row) > 0:  return True
        else: return False

    def is_group_admin(self, user_id, group_id):
        rows = self.user_group.find({'user_id': user_id, 'group_id': group_id})
        if len(rows) > 0 and rows[0]['is_admin']:  return True
        else: return False

    def is_member(self, user_id, group_id):
        rows = self.user_group.find({'user_id': user_id, 'group_id': group_id})
        if len(rows) > 0:  return True
        else: return False

    def is_permitted(self, params):
        params['all'] = True
        rows = self.find(params)
        print "permitted : %s" % rows
        if len(rows) == 0:  return False
        return True

    def add_permissions_to_group(self, resource_name, resource_id, permissions, to_group_id):
        group_permission_params = {
            "group_id": to_group_id,
            "resource": resource_name,
            "value": resource_id
        }
        for permission in permissions:
            group_permission_params["action"] = permission['action']
            if permission.get('condition'):
                group_permission_params['condition'] = permission['condition']
            self.permission.create(group_permission_params)

    def add_permissions_to_user(self, resource_name, resource_id, permissions, to_user_id):
        user_permission_params = {
            "user_id": to_user_id,
            "resource": resource_name,
            "value": resource_id
        }
        for permission in permissions:
            user_permission_params["action"] = permission['action']
            if permission.get('condition'):
                user_permission_params['condition'] = permission['condition']
            self.permission.create(user_permission_params)

    def create_permissions_to_group(self, user_id, resource_name, resource_id, permissions, to_group_id):

        # if this user is admin, allow it
        if self.is_admin(user_id):
            return self.add_permissions_to_group(resource_name, resource_id, permissions, to_group_id)

        # if this user has a permission to 'create' on this, allow it
        params = {
            'action': 'create',
            'resource': resource_name,
            'value': resource_id,
            'user_id': user_id
        }
        if self.is_permitted(params):
            return self.add_permissions_to_group(resource_name, resource_id, permissions, to_group_id)

        # if this user is admin of any group that has 'create' permission, allow it
        params = {
            'action': 'create',
            'resource': resource_name,
            'value': resource_id
        }
        permissions = self.find(params)
        permitted_group_ids = [ permission['group_id'] for permission in permissions if permission.get('group_id') ]
        from porper.models.user_group import UserGroup
        user_group = UserGroup(self.connection)
        user_groups = user_group.find({"user_id": user_id})
        admin_group_ids = [ user_group.group_id for user_group in user_groups if user_group.is_admin ]
        for group_id in admin_group_ids:
            if group_id in permitted_group_ids:
                return self.add_permissions_to_group(resource_name, resource_id, permissions, to_group_id)

        """
        # if this user is admin of the given group, allow it
        if self.permission_controller.is_group_admin(user_id, group_id):
            return _add_permissions_to_group(permissions, to_group_id)

        # if this user belongs to the given group, allow it
        from porper.models.user_group import UserGroup
        user_group = UserGroup(self.connection)
        user_groups = user_group.find({"user_id": user_id})



        if user_group in user_groups:
            return _add_permissions_to_group(permissions, to_group_id)
        """

        raise Exception("not permitted")

    def create_permissions_to_user(self, user_id, resource_name, resource_id, permissions, to_user_id):

        # no need to give permissions if the to_user_id is admin
        if self.is_admin(to_user_id):
            return

        # if this user is admin or equal to to_user_id, allow it
        if user_id == to_user_id or self.is_admin(user_id):
            return self.add_permissions_to_user(resource_name, resource_id, permissions, to_user_id)

        # if this user has a permission to 'create' on this, allow it
        params = {
            'action': 'create',
            'resource': resource_name,
            'value': resource_id,
            'user_id': user_id
        }
        if self.is_permitted(params):
            return self.add_permissions_to_user(resource_name, resource_id, permissions, to_user_id)

        raise Exception("not permitted")

    def create(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        #return self.permission.create(params)
        if params.get('to_group_id'):
            return self.create_permissions_to_group(user_id, params['resource_name'], params['resource_id'], params['permissions'], params['to_group_id'])
        elif params.get('to_user_id'):
            return self.create_permissions_to_user(user_id, params['resource_name'], params['resource_id'], params['permissions'], params['to_user_id'])

    def update(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        raise Exception("not supported")

    def delete(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.permission.delete(params)

    def _filter_conditions(self, user_id, rows):
        # if there is no permissions with conditions, return True
        permissions = [ permission for permission in rows if permission.get('condition') ]
        if len(permissions) == 0:   return rows
        filtered = [ permission for permission in rows if not permission.get('condition') ]
        for permission in permissions:
            condition = json.loads(permission['condition'])
            # check when the condition is 'is_admin' and it is satisified, add it to the return list if so
            if 'is_admin' in condition:
                if not user_id or not condition['is_admin'] or self.is_group_admin(user_id, permission.get('group_id')):
                    filtered.append(permission)
        return filtered

    def find(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return find_usin_user_id(user_id, params)

    def find_using_user_id(self, user_id, params):
        params['user_id'] = user_id
        rows = self.permission.find(params)
        return self._filter_conditions(user_id, rows)
