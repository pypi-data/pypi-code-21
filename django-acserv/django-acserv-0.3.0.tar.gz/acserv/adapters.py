class BaseAdapter:
    # banner的数据
    @classmethod
    def get_banner_context(cls, user):
        return {'cur_clients': 1, 'max_clients': 1}

    # 客户端超限后的数据
    @classmethod
    def get_exceed_clients_data_on_auth_success(cls, user):
        return []

    # device_id是否可以直接登录
    @classmethod
    def can_directly_login(cls, user, device_id):
        return False

    # 身份验证成功后, 处理保存device_id等, 并返回token
    @classmethod
    def get_token_on_auth_succeed(cls, request, auth_ctx, user):
        pass

    # 踢人时, 处理清理session等
    @classmethod
    def on_kick_session(cls, user, token_to_expire):
        pass
