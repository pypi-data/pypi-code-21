
ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class UserGroupController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.user import User
        from porper.models.group import Group
        from porper.models.user_group import UserGroup
        self.user = User(connection)
        self.group = Group(connection)
        self.user_group = UserGroup(connection)
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(connection)
        from porper.controllers.permission_controller import PermissionController
        self.permission_controller = PermissionController(self.connection)

    def find(self, access_key, params):
        if params.get('user_id'):
            return self.find_groups_by_user(access_key, params['user_id'])
        elif params.get('group_id'):
            return self.find_users_by_group(access_key, params['group_id'])
        return []

    """
    1. if this user is admin, return all found groups
    2. otherwise, return only the groups where both this user and given user belong
    """
    def find_groups_by_user(self, access_key, user_id):

        me = self.token_controller.find_user_id(access_token)

        # find all groups where the given user belongs
        user_groups = self.user_group.find({'user_id': user_id})
        print user_groups
        #group_ids = [ user_group['group_id'] for user_group in user_groups if user_group['is_admin'] ]
        group_ids = [ user_group['group_id'] for user_group in user_groups ]
        if len(group_ids) == 0: return []

        # if this user is admin, return all found groups
        if self.permission_controller.is_admin(me):
            params = {'ids': group_ids}
            print params
            return self.group.find(params)

        # return only the groups where this user belongs also
        my_user_groups = self.user_group.find({'user_id': me})
        print my_user_groups
        if len(my_user_groups) == 0: return []
        ids = []
        for my_user_group in my_user_groups:
            if my_user_group.group_id in group_ids:
                ids.append(my_user_group.group_id)
        if len(ids) == 0: return []
        params = {'ids': ids}
        print params
        return self.group.find(params)


    """
    if this user is admin or member of given group, return all users in the given group
    """
    def find_users_by_group(self, access_key, group_id):

        user_id = self.token_controller.find_user_id(access_token)

        if self.permission_controller.is_admin(user_id) or self.permission_controller.is_member(user_id, group_id):
            user_groups = self.user_group.find({'group_id': group_id})
            print user_groups
            user_ids = [ user_group['user_id'] for user_group in user_groups ]
            if len(user_ids) == 0: return []
            params = {'ids': user_ids}
            print params
            return self.user.find(params)

        return []
