
ADMIN_GROUP_ID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

class GroupController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.group import Group
        self.group = Group(connection)
        from porper.models.user_group import UserGroup
        self.user_group = UserGroup(connection)
        from porper.controllers.token_controller import TokenController
        self.token_controller = TokenController(connection)
        from porper.controllers.permission_controller import PermissionController
        self.permission_controller = PermissionController(self.connection)

    # only the admin can create a group
    def create(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.create_using_user_id(user_id, params)


    def create_using_user_id(self, user_id, params):
        if not self.permission_controller.is_admin(user_id):  raise Exception("not permitted")
        return self.group.create(params)

    def update(self, access_token, params):
        raise Exception("not supported")

    def delete(self, access_token, params):
        raise Exception("not supported")

    """
    1. return requested groups if I'm the admin
    2. if 'user_id' is given,
        - return all groups where both this user and given user belong
    3. otherwise, return all groups where this user belongs
    """
    def find(self, access_token, params):
        user_id = self.token_controller.find_user_id(access_token)
        return self.find_using_user_id(user_id, params)

    def find_using_user_id(self, user_id, params):

        # return all groups if I'm an admin
        if self.permission_controller.is_admin(user_id):
            if not params.get('user_id'):
                return self.group.find(params)
            else:
                user_groups = self.user_group.find({'user_id': params['user_id']})
                if len(user_groups) == 0:   return []
                group_ids = [ user_group['group_id'] for user_group in user_groups ]
                params['ids'] = group_ids
                del params['user_id']
                return self.group.find(params)

        # find all groups where this user belongs
        my_user_groups = self.user_group.find({'user_id': user_id})
        if len(my_user_groups) == 0:   return []
        my_group_ids = [ user_group['group_id'] for user_group in my_user_groups ]

        if params.get('user_id'):
            # now find all groups where the given user belongs
            user_groups = self.user_group.find({'user_id': params['user_id']})
            if len(user_groups) == 0:   return []
            del params['user_id']
            given_group_ids = [ user_group['group_id'] for user_group in user_groups ]
            group_ids = []
            # return all groups where both this user and given user belong
            for id in given_group_ids:
                if id in my_group_ids:
                    group_ids.append(id)
            if len(group_ids) == 0: return []
        else:
            # return all groups where this user belongs
            group_ids = my_group_ids

        params['ids'] = group_ids
        return self.group.find(params)
