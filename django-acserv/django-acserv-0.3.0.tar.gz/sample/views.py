from django.contrib.auth import get_user_model

from acserv.adapters import BaseAdapter

User = get_user_model()


class ACAdapter(BaseAdapter):
    # banner的数据
    @classmethod
    def get_banner_context(cls, user):
        return {'cur_clients': user.cur_clients, 'max_clients': user.max_clients}

    # 客户端超限后的数据
    @classmethod
    def get_exceed_clients_data_on_auth_success(cls, user):
        if user.cur_clients + 1 > user.max_clients:
            return [{'token': user.token, 'os': 'ios', 'app': 'client', 'created_time_ago': '3分钟前'},
                    {'token': user.token, 'os': 'win', 'app': 'client', 'created_time_ago': '7小时前'}]

    # 已有的device_id是否有效
    @classmethod
    def can_directly_login(cls, user, device_id):
        return User.objects.filter(device_id=device_id).exists()

    # 身份验证成功后, 处理client_session, 保存device_id等
    @classmethod
    def get_token_on_auth_succeed(cls, request, auth_ctx, user):
        user.device_id = auth_ctx.device_id
        user.cur_clients += 1
        user.save()
        return user.token

    # 踢人时, 处理清理session等
    @classmethod
    def on_kick_session(cls, user, token_to_expire):
        if user.token == token_to_expire:
            user.cur_clients -= 1
            user.save()
