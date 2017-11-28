from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from ipware.ip import get_ip

from acserv import proto
from acserv.views import BaseAdapter
from sample.models import ClientSession
from sample.serializers import ClientSessionSerializer

User = get_user_model()


class ACAdapter(BaseAdapter):
    @classmethod
    def can_skip_password(cls, auth_ctx, user):
        return ClientSession.objects.filter(device_id=auth_ctx.device_id, user=user).exists()

    @classmethod
    def remove_session(cls, user, device_id) -> str:
        cs = user.client_sessions.filter(device_id=device_id).first()
        if cs:
            cs_id = cs.id
            cs.delete()
            return str(cs_id)
        return None

    @classmethod
    def make_session_context_and_message(cls, request, auth_ctx, user):
        if not user.is_in_service():
            return None, '服务过期\n 请到baidu.com充值'

        client_session = user.client_sessions.create(ip=get_ip(request),
                                                     os=auth_ctx.platform + ' ' + auth_ctx.platform_version,
                                                     app='anyconnect')

        if auth_ctx.device_id:
            client_session.device_id = auth_ctx.device_id
            client_session.save()

        session_ctx = proto.SessionContext()
        session_ctx.id = str(client_session.id)
        session_ctx.user_pk = user.pk
        session_ctx.service_due = int(user.service_due.timestamp() * 1000)

        message = render_to_string('acserv/banner.txt',
                                   context={'service_due': user.service_due,
                                            'current_sessions': user.client_sessions.count(),
                                            'max_sessions': user.max_sessions})
        return session_ctx, message

    @classmethod
    def get_kick_session_options(cls, user):
        if user.client_sessions.count() + 1 > user.max_sessions:
            data = ClientSessionSerializer(instance=user.client_sessions, many=True).data
            for client in data:
                client['label'] = "{os} {app} ({created_time_ago})".format(**client)
                client['value'] = client.get('device_id')
            return data
