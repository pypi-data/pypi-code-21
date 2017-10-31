
import uuid
import json

ALL = "*"
ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class ResourceController():

    def __init__(self, account_id, region, permission_connection):
        self.account_id = account_id
        self.region = region
        self.connection = permission_connection
        self.resource = None
        self.model = None
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(self.connection)
        from porper.controllers.permission_controller import PermissionController
        self.permission_controller = PermissionController(self.connection)
        from porper.models.user_group import UserGroup
        self.user_group = UserGroup(self.connection)

    @property
    def model_name(self):
        return self.model.__class__.__name__

    """def _add_permissions_to_group(self, permission, to_group_id):
        group_permission_params = {
            "group_id": to_group_id,
            "resource": self.resource,
        }
        for permission in permissions:
            group_permission_params["value"] = permission['value']
            group_permission_params["action"] = permission['action']
            if permission.get('condition'):
                group_permission_params['condition'] = permission['condition']
            self.permission_controller.create(group_permission_params)

    def _add_permissions_to_user(self, permissions, to_user_id):
        user_permission_params = {
            "user_id": to_user_id,
            "resource": self.resource
        }
        for permission in permissions:
            user_permission_params["value"] = permission['value']
            user_permission_params["action"] = permission['action']
            if permission.get('condition'):
                user_permission_params['condition'] = permission['condition']
            self.permission_controller.create(user_permission_params)

    def add_permissions_to_group(self, access_token, permissions, to_group_id):

        user_id = self.token_controller.find_user_id(access_token)

        # if this user is admin, allow it
        if self.permission_controller.is_admin(user_id):
            return _add_permissions_to_group(permissions, to_group_id)

        # if this user has a permission to 'create' on this, allow it
        if self.permission_controller.is_permitted(params):
            return _add_permissions_to_group(permissions, to_group_id)

        # if this user is admin of any group that has 'create' permission, allow it
        params = {
            'action': action,
            'resource': self.resource,
            'value': id
        }
        permissions = self.permission_controller.find(params)
        permitted_group_ids = [ permission.group_id for permission in permission if permission.group_id ]
        from porper.models.user_group import UserGroup
        user_group = UserGroup(self.connection)
        user_groups = user_group.find({"user_id": user_id})
        admin_group_ids = [ user_group.group_id for user_group in user_groups if user_group.is_admin ]
        for group_id in admin_group_ids:
            if group_id in permitted_group_ids:
                return _add_permissions_to_group(permissions, to_group_id)

        raise Exception("not permitted")

    def add_permissions_to_user(self, access_token, permissions, to_user_id):

        # no need to give permissions if the to_user_id is admin
        if self.permission_controller.is_admin(to_user_id):
            return

        user_id = self.token_controller.find_user_id(access_token)

        # if this user is admin or equal to to_user_id, allow it
        if user_id == to_user_id or self.permission_controller.is_admin(user_id):
            return _add_permissions_to_user(permissions, to_user_id)

        # if this user has a permission to 'create' on this, allow it
        if self.permission_controller.is_permitted(params):
            return _add_permissions_to_user(permissions, to_user_id)

        raise Exception("not permitted")"""

    def find_permitted(self, user_id, action, id=None):
        if self.permission_controller.is_admin(user_id):
            # admin has all permissions
            return [{'value': ALL}]
        params = {
            'action': action,
            'resource': self.resource,
            'all': True
        }
        if id: params['value'] = id
        permissions = self.permission_controller.find_using_user_id(user_id, params)
        print 'permissions : %s' % permissions
        return permissions

    def is_permitted(self, user_id, action, id):
        if self.permission_controller.is_admin(user_id):
            return True
        params = {
            'action': action,
            'resource': self.resource,
            'all': True,
            'value': id
        }
        if not self.permission_controller.is_admin(user_id):
            params['user_id'] = user_id
        return self.permission_controller.is_permitted(params)

    def create(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.create_using_user_id(user_id, params)

    def create_using_user_id(self, user_id, params):

        # create a new item
        ret = self.model.create(params)
        print "%s is successfully created : %s" % (self.model_name, ret)

        permissions = [
            {'action': 'read'},
            {'action': 'create'},
            {'action': 'update'},
            {'action': 'delete'}
        ]

        # now add permissions to this user if this user is not admin
        # no need to give permissions if the user_id is admin
        if not self.permission_controller.is_admin(user_id):
            self.permission_controller.add_permissions_to_user(self.resource, ret['id'], permissions, user_id)

        # add permissions to the group where this user belongs
        condition = json.dumps({"is_admin": 1})
        permissions = [
            {'action': 'read'},
            {'action': 'create', 'condition': condition},
            {'action': 'update', 'condition': condition},
            {'action': 'delete', 'condition': condition}
        ]
        user_groups = self.user_group.find({'user_id': user_id})
        for user_group in user_groups:
            if user_group['group_id'] == ADMIN_GROUP_ID:    continue
            self.permission_controller.add_permissions_to_group(self.resource, ret['id'], permissions, user_group['group_id'])

        return ret

    def update(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.update_using_user_id(user_id, params)

    def update_using_user_id(self, user_id, params):
        if not self.is_permitted(user_id, 'update', params['id']):    raise Exception("not permitted")
        ret = self.model.update(params)
        print "%s [%s] is successfully updated : %s" % (self.model_name, params['id'], ret)
        return ret

    def delete(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.delete_using_user_id(user_id, params)

    def delete_using_user_id(self, user_id, params):
        if not self.is_permitted(user_id, 'delete', params['id']):    raise Exception("not permitted")
        ret = self.model.delete(params['id'])
        print "%s [%s] is successfully deleted : %s" % (self.model_name, params['id'], ret)
        return ret

    # find all read-permitted instances of the current resource, so 'id' is NOT given
    def find(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_using_user_id(user_id, params)

    def find_using_user_id(self, user_id, params):
        permissions = self.find_permitted(user_id, 'read')
        if len(permissions) == 0:   return []
        ids = [ permission['value'] for permission in permissions ]
        if params is None:
            if ALL not in ids:
                return self.model.find_by_ids(ids)
            else:
                return self.model.find({})
        elif params.get('id'):
            if ALL in ids or params['id'] in ids:
                return self.model.find(params)
            else:
                return []
        elif params.get('ids'):
            if ALL in ids:
                return self.model.find(params)
            else:
                permitted_ids = [id for id in params['ids'] if id in ids]
                if len(permitted_ids) == 0:
                    return []
                else:
                    params['ids'] = permitted_ids
                    return self.model.find(params)
        else:
            if ALL not in ids:
                params['ids'] = ids
            return self.model.find(params)

    # find one read-permitted instance of the current resource whose id is the given
    def find_by_id(self, access_token, id):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_by_id_using_user_id(user_id, id)

    def find_by_id_using_user_id(self, user_id, id):
        permissions = self.find_permitted(user_id, 'read', id)
        if len(permissions) == 0:   return None
        for permission in permissions:
            if permission['value'] == id or permission['value'] == ALL:
                return self.model.find_by_id(id)
        return None

    def find_by_ids(self, access_token, params_ids):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_by_ids_using_user_id(user_id, ids)

    def find_by_ids_using_user_id(self, user_id, ids):
        permissions = self.find_permitted(user_id, 'read')
        if len(permissions) == 0:   return []
        ids = [ permission['value'] for permission in permissions ]
        if ALL in ids:
            return self.model.find_by_ids(params_ids)
        else:
            permitted_ids = [id for id in params_ids if id in ids]
            if len(permitted_ids) == 0:
                return []
            else:
                return self.model.find_by_ids(permitted_ids)
