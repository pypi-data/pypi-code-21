import base64
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import List, Tuple

import pydash as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import SimpleLazyObject
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acserv import proto
from acserv.helpers import base64_to_proto, proto_to_base64

User = get_user_model()

VERSIONS_CAN_HIDE_USERNAME = [
    "4.2.03013",  # win&mac
    "4.0.05069",  # ios
    "4.0.05057"  # android
]


def get_adapter():
    settings_adapter = _.get(settings, 'ANYCONNECT.ADAPTER')
    if settings_adapter:
        import importlib
        tokens = settings_adapter.split('.')
        pkg = importlib.import_module('.'.join(tokens[:-1]))
        return getattr(pkg, tokens[-1])
    else:
        return BaseAdapter


class BaseAdapter:
    @classmethod
    def can_skip_password(cls, auth_ctx, user) -> bool:
        """ 账号验证后，是否可以跳过密码过程 """
        return False

    @classmethod
    def remove_session(cls, user, device_id) -> str:
        """清理session，返回 id，供go来踢人"""
        pass

    @classmethod
    def make_session_context_and_message(cls, request, auth_ctx, user) -> Tuple[proto.SessionContext, str]:
        """ 身份验证成功后, 判断service_due等, 并生成session_context，acserv会将内容打包放在 webvpn cookie中，供go识别 """
        raise NotImplementedError

    @classmethod
    def get_kick_session_options(cls, user) -> List:
        """ 客户端超过限制后form中的option条目 """
        return [
            # {value, label},
        ]


@method_decorator(csrf_exempt, name='dispatch')
class ACView(View):
    # 为True的view会重新生成auth_context而不从cookie中读取，一般用在Index上
    reset_auth_context = False

    adapter = SimpleLazyObject(get_adapter)  # url引入view时会有顺序问题而报错

    def dispatch(self, request, *args, **kwargs):
        # 如果提供了验证头的配置，就一定要匹配，否则403
        AUTH_HEADER = _.get(settings, 'ANYCONNECT.AUTH_HEADER')
        if AUTH_HEADER:
            for k, v in AUTH_HEADER.items():
                meta_key = 'HTTP_{}'.format(k.replace('-', '_').upper())
                if request.META.get(meta_key) == v:
                    break
            else:
                return HttpResponseForbidden()

        # 在正式处理请求之前，生成或获得auth_ctx
        if self.reset_auth_context:
            auth_ctx = self.make_auth_context(request)
        else:
            auth_ctx, resp = self.get_auth_context_or_response(request)
            if resp:
                return resp

        resp = super(ACView, self).dispatch(request, auth_ctx, *args, **kwargs)

        # 在请求处理之后，追加更新后的auth_ctx
        self.attach_auth_context(resp, auth_ctx)

        return resp

    @classmethod
    def make_auth_context(cls, request):
        auth_context = proto.AuthContext()
        auth_context.uid = str(uuid.uuid4())
        auth_context.user_agent = request.META.get('HTTP_USER_AGENT')

        root = ET.fromstring(request.body)
        node = root.find('device-id')
        if node is not None:
            auth_context.device_id = node.get('unique-id') or ''
            auth_context.device_type = node.get('device-type') or ''
            auth_context.platform = node.text or request.META.get('HTTP_X_acserv_IDENTIFIER_PLATFORM') or ''
            auth_context.platform_version = node.get('platform-version') or ''

        node = root.find('version')
        if node is not None:
            auth_context.client_version = node.text

        node = root.find('phone-id')
        if node is not None:
            auth_context.device_imei = node.text

        node = root.find('mac-address-list')
        if node is not None:
            auth_context.device_mac = ','.join([x.text for x in node.findall('mac-address')])

        return auth_context

    @classmethod
    def get_auth_context_or_response(cls, request):
        try:
            s = request.COOKIES['webvpncontext']
            auth_ctx = base64_to_proto(s, proto.AuthContext)
            assert auth_ctx, 'must valid'

            return auth_ctx, None
        except Exception as e:
            return None, HttpResponse(status=401)

    @classmethod
    def get_user_or_response(cls, request, auth_ctx):
        if not auth_ctx or not auth_ctx.user_pk:
            return None, cls.render_account_form(request,
                                                 message=render_to_string('acserv/messages/account_required.txt'))

        user = User.objects.filter(pk=auth_ctx.user_pk).first()
        if user:
            return user, None
        else:
            return None, cls.render_account_form(request,
                                                 message=render_to_string('acserv/messages/account_not_found.txt'))

    @classmethod
    def handle_auth_succeed(cls, request, auth_ctx, user):
        cls.adapter.remove_session(user, auth_ctx.device_id)

        options = cls.adapter.get_kick_session_options(user)
        if options:
            return cls.render_kick_session_form(
                request, options,
                message=render_to_string('acserv/messages/sessions_too_many.txt'),
                can_hide_username=auth_ctx.client_version in VERSIONS_CAN_HIDE_USERNAME
            )

        session_context, message = cls.adapter.make_session_context_and_message(request, auth_ctx, user)

        if session_context:
            session_key = proto_to_base64(session_context)
        else:
            session_key = 'rejected'  # acserv收到之后会无法解析这个key而拒绝连接

        return cls.render_result_view(request, message, session_key)

    @classmethod
    def render_xml(cls, request, template_name, **context):
        resp = render(request, template_name, context)
        resp["X-transcend-Version"] = '1'
        resp["Content-Type"] = "text/xml"
        return resp

    @classmethod
    def attach_auth_context(cls, response, auth_ctx):
        response.set_cookie('webvpncontext',
                            proto_to_base64(auth_ctx),
                            expires=timezone.now() + timedelta(1),
                            path='/',
                            secure=True)
        return response

    @classmethod
    def render_account_form(cls, request, message):
        return cls.render_xml(request, 'acserv/account.xml',
                              message=message)

    @classmethod
    def render_password_form(cls, request, message):
        return cls.render_xml(request, 'acserv/password.xml',
                              message=message)

    @classmethod
    def render_kick_session_form(cls, request, options, message, can_hide_username=False):
        """ 踢出多余的客户端 """
        return cls.render_xml(request, 'acserv/kick_session.xml',
                              options=options,
                              message=message,
                              can_hide_username=can_hide_username)

    @classmethod
    def render_result_view(cls, request, message, session_key=''):
        resp = cls.render_xml(request, 'acserv/success.xml', message=message)
        resp.set_cookie('webvpn', session_key, secure=True)
        return resp

    @classmethod
    def attach_ac_command(cls, res, kind, payload):
        obj = {"kind": kind, "payload": payload}
        s = base64.urlsafe_b64encode(json.dumps(obj).encode())
        res["X-Ac-Command"] = s
        return s


class IndexACView(ACView):
    reset_auth_context = True

    def post(self, request, auth_ctx):
        if not auth_ctx.device_id:
            return self.render_result_view(request,
                                           message=render_to_string('acserv/messages/index_missing_device_id.txt'))
        return self.render_account_form(request,
                                        message=render_to_string('acserv/messages/account_required.txt'))


class UsernameACView(ACView):
    def post(self, request, auth_ctx):
        # 账号未输入
        username = self.request.POST.get('username', '').lower()
        if not username:
            return self.render_account_form(request,
                                            message=render_to_string('acserv/messages/account_required.txt'))

        # 用户不存在
        user = User.objects.filter(username=username).first()
        if not user:
            return self.render_account_form(request,
                                            message=render_to_string('acserv/messages/account_not_found.txt'))

        auth_ctx.user_pk = user.pk

        # 有上次登录记录的，直接登录
        if self.adapter.can_skip_password(auth_ctx, user):
            return self.handle_auth_succeed(request, auth_ctx, user)

        # 没有登录记录的，提示输入密码
        return self.render_password_form(request,
                                         message=render_to_string('acserv/messages/password_required.txt'))


class PasswordACView(ACView):
    def post(self, request, auth_ctx):
        user, resp = self.get_user_or_response(request, auth_ctx)
        if resp:
            return resp

        # 密码未输
        password = request.POST.get('password')
        if not password:
            return self.render_password_form(request,
                                             message=render_to_string('acserv/messages/password_required.txt'))

        # 密码不正确
        if not user.check_password(password):
            return self.render_password_form(request,
                                             message=render_to_string('acserv/messages/password_wrong.txt'))

        return self.handle_auth_succeed(request, auth_ctx, user)


class KickSessionACView(ACView):
    def post(self, request, auth_ctx):
        user, resp = self.get_user_or_response(request, auth_ctx)
        if resp:
            return resp

        device_id = request.POST.get('group_list', '')
        id = self.adapter.remove_session(user, device_id)  # todo: kick失败的处理逻辑

        res = self.handle_auth_succeed(request, auth_ctx, user)
        self.attach_ac_command(res, "kick_session", id)
        return res


class LogoutACView(ACView):
    # 显示banner时，如果拒绝，就进入这里
    def get(self, request, auth_ctx):
        return HttpResponse('ok')
