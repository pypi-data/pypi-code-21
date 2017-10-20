import uuid
import xml.etree.ElementTree as ET
from datetime import timedelta

import pydash as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acserv import proto
from acserv.helpers import base64_to_proto, proto_to_base64

User = get_user_model()

DEFAULT_MESSAGES = {
    'account': {
        'required': '请输入帐号',
        'not_exists': '未找到该用户，请重新输入邮箱账号',
        'not_in_service': '尚未购买服务，或服务已过期',
    },
    'password': {
        'required': '请输入密码',
        'wrong': '密码不正确, 请重新输入',
    },
    'client_exceed': '已经达到同时在线个数限制，请选择您所要替换的客户端',
}


def message_or_default(key_path):
    messages = _.get(settings, 'ANYCONNECT.FORM_MESSAGES')
    message = _.get(messages, key_path, _.get(DEFAULT_MESSAGES, key_path))
    assert message, '找不到{}, 缺少默认配置或key不正确'.format(key_path)
    return message


def get_adapter():
    settings_adapter = _.get(settings, 'ANYCONNECT.ADAPTER')
    if settings_adapter:
        import importlib
        tokens = settings_adapter.split('.')
        pkg = importlib.import_module('.'.join(tokens[:-1]))
        return getattr(pkg, tokens[-1])
    else:
        from acserv.adapters import BaseAdapter
        return BaseAdapter


@method_decorator(csrf_exempt, name='dispatch')
class ACView(View):
    # 为True的view会重新生成auth_context而不从cookie中读取，一般用在Index上
    reset_auth_context = False

    adapter = get_adapter()

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
            return None, cls.render_account_form(request, message_or_default('account.required'))

        user = User.objects.filter(pk=auth_ctx.user_pk).first()
        if user:
            return user, None
        else:
            return None, cls.render_account_form(request, message_or_default('account_not_exists'))

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
    def render_clients_form(cls, request, data, message):
        for client in data:
            client['label'] = "{os} {app} ({created_time_ago})".format(**client)

        return cls.render_xml(request, 'acserv/clients.xml',
                              clients=data,
                              message=message)

    @classmethod
    def render_auth_succeed(cls, request, auth_ctx, user):
        if not user.is_in_service():
            return cls.render_account_form(request, message_or_default('account.not_in_service'))

        exceed_clients_data = cls.adapter.get_exceed_clients_data_on_auth_success(user)
        if exceed_clients_data:
            return cls.render_clients_form(request, exceed_clients_data, message_or_default('client_exceed'))

        token = cls.adapter.get_token_on_auth_succeed(request, auth_ctx, user)

        # client_ctx -> client_key，保存到cookie中，代理根据这个数据识别用户和用户服务期
        client_ctx = proto.SessionContext()
        client_ctx.token = token
        client_ctx.user_pk = user.pk
        client_ctx.service_due = int(user.service_due.timestamp() * 1000)

        client_key = proto_to_base64(client_ctx)

        context = {'service_due': user.service_due}
        context.update(cls.adapter.get_banner_context(user))
        banner = render_to_string('acserv/banner.html', context=context)

        resp = cls.render_xml(request, 'acserv/success.xml',
                              banner=banner)
        resp.set_cookie('webvpn', client_key, secure=True)

        return resp


class IndexACView(ACView):
    reset_auth_context = True

    def post(self, request, auth_ctx):
        return self.render_account_form(request, message_or_default('account.required'))


class UsernameACView(ACView):
    def post(self, request, auth_ctx):
        # 账号未输入
        username = self.request.POST.get('username', '').lower()
        if not username:
            return self.render_account_form(request, message_or_default('account.required'))

        # 用户不存在
        user = User.objects.filter(username=username).first()
        if not user:
            return self.render_account_form(request, message_or_default('account.not_exists'))

        auth_ctx.user_pk = user.pk

        # 有上次登录记录的，直接登录
        if auth_ctx.device_id and self.adapter.can_directly_login(user, auth_ctx.device_id):
            return self.render_auth_succeed(request, auth_ctx, user)

        # 没有登录记录的，提示输入密码
        return self.render_password_form(request, message_or_default('password.required'))


class PasswordACView(ACView):
    def post(self, request, auth_ctx):
        user, resp = self.get_user_or_response(request, auth_ctx)
        if resp:
            return resp

        # 密码未输
        password = request.POST.get('password')
        if not password:
            return self.render_password_form(request, message_or_default('password.required'))

        # 密码不正确
        if not user.check_password(password):
            return self.render_password_form(request, message_or_default('password.wrong'))

        return self.render_auth_succeed(request, auth_ctx, user)


class KickSessionACView(ACView):
    def post(self, request, auth_ctx):
        user, resp = self.get_user_or_response(request, auth_ctx)
        if resp:
            return resp

        token_to_expire = request.POST.get('group_list', '')
        self.adapter.on_kick_session(user, token_to_expire)

        return self.render_auth_succeed(request, auth_ctx, user)


class LogoutACView(ACView):
    # 显示banner时，如果拒绝，就进入这里
    def get(self, request, auth_ctx):
        return HttpResponse('ok')
