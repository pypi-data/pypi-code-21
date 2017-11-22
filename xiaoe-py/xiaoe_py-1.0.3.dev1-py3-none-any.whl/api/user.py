from xiaoe.type import UserRegisterData, UserQueryData, UserUpdateData


class User(object):
    @classmethod
    def register(cls, user_register_data: UserRegisterData, poster):
        path = '/users.register/'
        return poster.post(path, user_register_data.data)

    @classmethod
    def query(cls, user_query_data: UserQueryData, poster):
        path = '/users.getinfo/'
        return poster.post(path, user_query_data.data)

    @classmethod
    def update(cls, user_update_data: UserUpdateData, poster):
        path = '/users.modifyinfo/'
        return poster.post(path, user_update_data.data)
