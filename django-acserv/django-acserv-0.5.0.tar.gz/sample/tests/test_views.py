from copy import copy
from datetime import timedelta

import pydash as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings
from django.utils import timezone

from acserv import proto
from acserv.helpers import base64_to_proto
from acserv.views import ACView, IndexACView

User = get_user_model()

INDEX_BODY = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
              b'<config-auth client="vpn" type="init" aggregate-auth-version="2">\n'
              b'<version who="vpn">4.0.05069</version>\n'
              b'<device-id device-type="iPhone8,1" platform-version="10.3.3" unique-id="0b1726e825960936d76adf6caf004b97e35a7760">apple-ios</device-id>\n'
              b'<phone-id>unknown</phone-id>\n'
              b'<group-select>MacBookPro11,3(mac-intel 10.12.1)</group-select>\n'
              b'<group-access>https://192.168.31.244</group-access>\n'
              b'</config-auth>\n')

INDEX_META = {
    'CONTENT_TYPE': 'application/x-www-form-urlencoded',
    'HTTP_ACCEPT': '*/*',
    'HTTP_ACCEPT_ENCODING': 'identity',
    'HTTP_CONNECTION': 'close,close',
    'HTTP_HOST': '192.168.31.244',
    'HTTP_PROXY': '192.168.31.244',
    'HTTP_USER_AGENT': 'AnyConnect AppleSSLVPN_Darwin_ARM (iPhone) 4.0.05069',
    'HTTP_X_AGGREGATE_AUTH': '1',
    'HTTP_X_ANYCONNECT_IDENTIFIER_CLIENTVERSION': '4.0.05069',
    'HTTP_X_ANYCONNECT_IDENTIFIER_DEVICETYPE': 'iPhone8,1',
    'HTTP_X_ANYCONNECT_IDENTIFIER_DEVICE_IMEI': 'unknown',
    'HTTP_X_ANYCONNECT_IDENTIFIER_DEVICE_MACADDRESS': 'unknown',
    'HTTP_X_ANYCONNECT_IDENTIFIER_DEVICE_UNIQUEID': '0b1726e825960936d76adf6caf004b97e35a7760',
    'HTTP_X_ANYCONNECT_IDENTIFIER_PLATFORM': 'apple-ios',
    'HTTP_X_ANYCONNECT_IDENTIFIER_PLATFORMVERSION': '10.3.3',
    'HTTP_X_FORWARDED_FOR': '10.0.2.2',
    'HTTP_X_PASSCODE': 'hello',
    'HTTP_X_TRANSCEND_VERSION': '1,1',
    'QUERY_STRING': '',
    'REMOTE_ADDR': '192.168.31.244',
    'REMOTE_PORT': '55192',
}

USERNAME_BODY = b'username=a%40a.aa'
USERNAME_META = copy(INDEX_META)
USERNAME_META.update({
    'HTTP_COOKIE': 'webvpnc=bu:/&p:t&iu:1/&sh:369B0AE7D129B6F0B74616340D96EA2D74FA9747; '
                   'webvpncontext=CiQzZjQyODYyNi1kMTNhLTQ1NGMtYTk2NS0zNjA4ODA5MmY4NGEaKDBiMTcyNmU4MjU5NjA5MzZkNzZhZGY2Y2FmMDA0Yjk3ZTM1YTc3NjAiCWlQaG9uZTgsMTIHdW5rbm93bjoJYXBwbGUtaW9zQgYxMC4zLjNKCTQuMC4wNTA2OVI0QW55Q29ubmVjdCBBcHBsZVNTTFZQTl9EYXJ3aW5fQVJNIChpUGhvbmUpIDQuMC4wNTA2OQ==',
})

PASSWORD_BODY = b'password=password'


def override_auth_header(val):
    return _.merge({}, settings.ANYCONNECT, {'AUTH_HEADER': val})


@override_settings(ANYCONNECT=override_auth_header({'auth-header': 'hello'}))
class ACViewTest(TestCase):
    def test_make_auth_context(self):
        req = RequestFactory().post('/',
                                    data=INDEX_BODY,
                                    content_type="application/x-www-form-urlencoded",
                                    HTTP_AUTH_HEADER='hello',
                                    **INDEX_META)
        req.session = {}
        ctx = IndexACView.make_auth_context(req)

        self.assertIsNotNone(ctx.uid, '随机生成')
        self.assertEqual(ctx.device_id, "0b1726e825960936d76adf6caf004b97e35a7760")
        self.assertEqual(ctx.device_type, "iPhone8,1")
        self.assertEqual(ctx.device_imei, "unknown")
        self.assertEqual(ctx.platform, "apple-ios")
        self.assertEqual(ctx.platform_version, "10.3.3")
        self.assertEqual(ctx.client_version, "4.0.05069")
        self.assertEqual(ctx.user_agent, "AnyConnect AppleSSLVPN_Darwin_ARM (iPhone) 4.0.05069")

    def test_auth_header(self):
        req = RequestFactory().get('/')
        resp = ACView.as_view()(req)
        self.assertEqual(resp.status_code, 403)

        req = RequestFactory().get('/', HTTP_AUTH_HEADER='hello')
        resp = ACView.as_view()(req)
        self.assertEqual(resp.status_code, 401, '带合法头就不会403')

    def test_get_auth_context_or_response(self):
        req = RequestFactory().post('/',
                                    data=INDEX_BODY,
                                    content_type="application/x-www-form-urlencoded",
                                    **INDEX_META)
        auth_ctx, resp = ACView.get_auth_context_or_response(req)
        self.assertIsNotNone(resp)

        req = RequestFactory().post('/',
                                    data=USERNAME_BODY,
                                    content_type="application/x-www-form-urlencoded",
                                    **USERNAME_META)
        auth_ctx, resp = ACView.get_auth_context_or_response(req)
        self.assertIsNone(resp)
        self.assertEqual(auth_ctx.device_id, '0b1726e825960936d76adf6caf004b97e35a7760')

    def test_get_user_or_response(self):
        req = RequestFactory().post('/',
                                    data=USERNAME_BODY,
                                    content_type="application/x-www-form-urlencoded",
                                    **USERNAME_META)
        auth_ctx, _ = ACView.get_auth_context_or_response(req)

        user, resp = ACView.get_user_or_response(req, auth_ctx)
        self.assertIsNone(user)
        self.assertIsNotNone(resp)

        user = User.objects.create_user('a@a.aa', 'password')
        auth_ctx.user_pk = user.pk
        user, resp = ACView.get_user_or_response(req, auth_ctx)
        self.assertIsNotNone(user)
        self.assertIsNone(resp)


@override_settings(ROOT_URLCONF='acserv.urls',
                   ANYCONNECT=override_auth_header(None))
class IndexACViewTest(TestCase):
    def test_post(self):
        client = Client()

        resp = client.post('/',
                           data=INDEX_BODY,
                           content_type="application/x-www-form-urlencoded",
                           **INDEX_META)
        self.assertTrue('webvpncontext' in resp.cookies)

        auth_ctx = base64_to_proto(resp.cookies['webvpncontext'].value, proto.AuthContext)
        self.assertIsNotNone(auth_ctx.uid, 'webvpncontext是一个pb的message')


@override_settings(ROOT_URLCONF='acserv.urls',
                   ANYCONNECT=override_auth_header(None))
class LoginACViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='a@a.aa',
            email='a@a.aa',
            password='password',
            service_due=timezone.now() + timedelta(100))

    def test_post(self):
        client = Client()

        resp = client.post('/',
                           data=INDEX_BODY,
                           content_type="application/x-www-form-urlencoded",
                           **INDEX_META)

        resp = client.post('/auth/username',
                           data=USERNAME_BODY,
                           content_type="application/x-www-form-urlencoded",
                           )

        resp = client.post('/auth/password',
                           data=PASSWORD_BODY,
                           content_type="application/x-www-form-urlencoded",
                           )
        self.assertContains(resp, "<auth id=\"success\">")

        # 再次登录免输密码
        client2 = Client()
        client2.post('/',
                     data=INDEX_BODY,
                     content_type="application/x-www-form-urlencoded",
                     **INDEX_META)
        resp = client2.post('/auth/username',
                            data=USERNAME_BODY,
                            content_type="application/x-www-form-urlencoded",
                            )
        self.assertContains(resp, "<auth id=\"success\">")

    def test_exceed_max_sessions(self):
        self.user.max_sessions = 1
        self.user.current_sessions = 1
        self.user.save()

        client = Client()
        client.post('/', data=INDEX_BODY, content_type='application/x-www-form-urlencoded', **INDEX_META)
        client.post('/auth/username', data=USERNAME_BODY, content_type='application/x-www-form-urlencoded')
        resp = client.post('/auth/password', data=PASSWORD_BODY, content_type='application/x-www-form-urlencoded')
        self.assertTrue('group_list' in resp.content.decode('utf-8'), '提示要踢一个客户端')

        self.user.max_sessions = 2
        self.user.save()

        client.post('/', data=INDEX_BODY, content_type='application/x-www-form-urlencoded', **INDEX_META)
        client.post('/auth/username', data=USERNAME_BODY, content_type='application/x-www-form-urlencoded')
        resp = client.post('/auth/password', data=PASSWORD_BODY, content_type='application/x-www-form-urlencoded')
        self.assertFalse('group_list' in resp.content.decode('utf-8'), '最大客户端数超过已登录客户端，不提示踢人')


@override_settings(ROOT_URLCONF='acserv.urls',
                   ANYCONNECT=override_auth_header(None))
class KickSessionACViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('a@a.aa',
                                             email='a@a.aa',
                                             password='password',
                                             service_due=timezone.now() + timedelta(100))

    def test(self):
        token = 'abc'
        self.user.current_sessions = 2
        self.user.max_sessions = 2
        self.user.token = token
        self.user.save()

        client = Client()
        client.post('/', data=INDEX_BODY, content_type='application/x-www-form-urlencoded', **INDEX_META)
        client.post('/auth/username', data=USERNAME_BODY, content_type='application/x-www-form-urlencoded')
        resp = client.post('/auth/password', data=PASSWORD_BODY, content_type='application/x-www-form-urlencoded')
        self.assertTrue('group_list' in resp.content.decode('utf-8'), '提示要踢一个客户端')

        resp = client.post('/auth/clients',
                           data="group_list={}".format('no such token'),
                           content_type='application/x-www-form-urlencoded')
        self.assertTrue('group_list' in resp.content.decode('utf-8'), '要踢的login_token不对，踢失败，继续显示踢人界面')

        resp = client.post('/auth/clients',
                           data="group_list={}".format(self.user.token),
                           content_type='application/x-www-form-urlencoded')

        self.assertTrue('success' in resp.content.decode('utf-8'), '踢人之后登录成功')
        self.assertEqual(self.user.current_sessions, 2, '去掉一个，加上一个，还是2个')
