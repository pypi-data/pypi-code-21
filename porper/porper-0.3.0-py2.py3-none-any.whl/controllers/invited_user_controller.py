
from datetime import datetime

ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class InvitedUserController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.invited_user import InvitedUser
        self.invited_user = InvitedUser(connection)
        from porper.models.user_group import UserGroup
        self.user_group = UserGroup(connection)
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(connection)
        from porper.controllers.permission_controller import PermissionController
        self.permission_controller = PermissionController(self.connection)

    def create(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.create_using_user_id(user_id, params)

    def create_using_user_id(self, user_id, params):

        # allowed if I'm an admin
        if self.permission_controller.is_admin(user_id):
            return self._save(user_id, params)

        # allowed if I'm the group admin of the given group
        group_id = params['group_id']
        if self.permission_controller.is_group_admin(user_id, group_id):
            return self._save(user_id, params)

        raise Exception("not permitted")

    def _save(self, user_id, params):
        invited_users = self.invited_user.find(params)
        if len(invited_users) > 0:
            print 'already invited'
            return True
        if not params.get('invited_by'):
            params['invited_by'] = user_id
        if not params.get('invited_at'):
            params['invited_at'] = str(datetime.utcnow())
        if not params.get('state'):
            params['state'] = self.invited_user.INVITED
        if not params.get('is_admin'):
            params['is_admin'] = False
        else:
            params['is_admin'] = True
        return self.invited_user.create(params)

    def update(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.update_using_user_id(user_id, params)

    def update_using_user_id(self, user_id, params):

        # allowed if I'm an admin
        if self.permission_controller.is_admin(user_id):
            return self.invited_user.update(params)

        # allowed if I'm the group admin of the given group
        group_id = params['group_id']
        if self.permission_controller.is_group_admin(user_id, group_id):
            return self.invited_user.update(params)

        raise Exception("not permitted")

    """
    1. return all invited users if I'm the admin
    2. if 'group_id' is given,
        - return all invited users of a given group if I'm the admin of given group
    3. otherwise,
        - return all invited users of groups where I'm the group admin
    """
    def find(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_using_user_id(user_id, params)

    def find_using_user_id(self, user_id, params):

        # return all invited users if I'm an admin
        if self.permission_controller.is_admin(user_id):  return self.invited_user.find(params)

        if not params.get('group_id'):
            # return all invited users of groups where I'm the group admin
            user_groups = self.user_group.find({'user_id': user_id})
            group_ids = [ user_group['group_id'] for user_group in user_groups if user_group['is_admin'] ]
            if len(group_ids) > 0:
                params['group_ids'] = group_ids
                return self.invited_user.find(params)
        else:
            # return all invited users of the given group if I'm the group admin
            if self.permission_controller.is_group_admin(user_id, group_id):
                return self.invited_user.find(params)

        raise Exception("not permitted")
