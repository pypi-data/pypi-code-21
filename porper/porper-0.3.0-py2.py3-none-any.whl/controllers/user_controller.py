
ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class UserController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.user import User
        from porper.models.user_group import UserGroup
        from porper.models.invited_user import InvitedUser
        self.user = User(connection)
        self.user_group = UserGroup(connection)
        self.invited_user = InvitedUser(connection)
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(connection)
        from porper.controllers.permission_controller import PermissionController
        self.permission_controller = PermissionController(self.connection)

    def create(self, access_token, params):

        # if this is the first user, save it as an admin
        users = self.user.find({})
        if len(users) == 0:
            # set this user to the admin
            self.user.create(params)
            self.user_group.create({'user_id': params['id'], 'group_id': ADMIN_GROUP_ID})
            return params['id']

        user_id = self.token_controller.find_user_id(access_token)
        return self.create_using_user_id(user_id, params)

    def create_using_user_id(self, user_id, params):

        # add a user to a group if I'm an admin or the group admin of the given group
        if params.get('group_id'):
            if self.permission_controller.is_admin(user_id) or self.permission_controller.is_group_admin(user_id, params.get('group_id')):
                self.user_group.create(params)
                return user_id
            else:
                raise Exception("not permitted")

        if not self.permission_controller.is_admin(user_id):
            raise Exception("not permitted")

        rows = self.user.find(params)
        if len(rows) > 0:
            print 'already exists'
            return rows[0]['id']

        # add the user if this user was invited before
        invited_users = self.invited_user.find({'email':params['email'], 'auth_type':params['auth_type']})
        if len(invited_users) == 1:
            invited_user = invited_users[0]
            self.user.create(params)
            self.user_group.create({'user_id': params['id'], 'group_id': invited_user['group_id'], 'is_admin': invited_user['is_admin']})
            self.invited_user.update({'email':params['email'], 'auth_type':params['auth_type'], 'state':self.invited_user.REGISTERED})
            return params['id']
        else:
            #self.user.create(params)
            #return params['id']
            raise Exception("not permitted")

    def delete(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.delete_using_user_id(user_id, params)

    def delete_using_user_id(self, user_id, params):

        # remove a user from a group if I'm an admin or the group admin of the given group
        if params.get('group_id'):
            if self.permission_controller.is_admin(user_id) or self.permission_controller.is_group_admin(user_id, params.get('group_id')):
                self.user_group.delete(params)
                return user_id
            else:
                raise Exception("not permitted")

        if self.permission_controller.is_admin(user_id):
            self.user.delete(params)
            return user_id
        else:
            raise Exception("not permitted")

    """
    1. return requested users if I'm the admin
    2. if 'group_id' is given,
        - return all members of the given group if I belong to that group
    3. otherwise,
        - return all users of groups where I belong
    """
    def find(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_using_user_id(user_id, params)

    def find_using_user_id(self, user_id, params):

        # return all users if I'm an admin
        if self.permission_controller.is_admin(user_id):
            if not params.get('group_id'):
                return self.user.find(params)
            else:
                user_groups = self.user_group.find({'group_id': params['group_id']})
                if len(user_groups) == 0:   return []
                user_ids = [ user_group['user_id'] for user_group in user_groups ]
                params['ids'] = user_ids
                del params['group_id']
                return self.user.find(params)

        # return all members of the given group if I'm a member of the given group
        if params.get('group_id'):
            if self.permission_controller.is_member(user_id, params['group_id']):
                user_groups = self.user_group.find({'group_id': params['group_id']})
                if len(user_groups) == 0:   return []
                user_ids = [ user_group['user_id'] for user_group in user_groups ]
                params['ids'] = user_ids
                del params['group_id']
                return self.user.find(params)
            else:
                return []

        # return all users of groups where I belong
        user_groups = self.user_group.find({'user_id': user_id})
        group_ids = [ user_group['group_id'] for user_group in user_groups ]
        if len(group_ids) == 0:
            # if no group is found, return only itself
            params['id'] = user_id
        else:
            user_groups = self.user_group.find_by_group_ids(group_ids)
            user_ids = [ user_group['user_id'] for user_group in user_groups ]
            params['ids'] = user_ids
        return self.user.find(params)
