from rest_framework.response import Response
from django.template.response import SimpleTemplateResponse
from django.utils import six
from django.utils.six.moves.http_client import responses
import platform

from rest_framework.serializers import Serializer
from enum import Enum
class APIResponse(Enum):
    NOT_INITIALIZED = "not-initialized"
    SUCCESS = "success"
    FAIL = "fail"
    UNAUTHORIZED_SERVICE_INVOKER = "unauthorized-invoker"
    VALIDATION_FAIL = "validation-fail"
    BAD_PARAMETER = "bad-parameter"
    UNAUTHORIZED = "unauthorized"
    USER_NOT_LOGIN = "user-not-login"
    RPC_FAIL = "rpc-fail"
    NOT_FOUND = "not found"

class APIResponseMessage(Enum):
    SUCCESS = 'API调用成功'
    FAIL = 'API调用失败'
    UNAUTHORIZED_SERVICE_INVOKER = '拒绝访问,未授权的服务调用者'
    VALIDATION_FAIL = '请求参数验证失败'
    BAD_PARAMETER = '拒绝访问,请求参数错误'
    UNAUTHORIZED = '拒绝访问,您没有权限请求该资源'
    NOT_INITIALIZED = '返回值未初始化'
    USER_NOT_LOGIN = '用户未登陆'
    RPC_FAIL = '远程调用失败【{0}】'
    NOT_FOUND = "资源不存在"

class APIResponseHTTPCode(Enum):
    SUCCESS = 200
    FAIL = 400
    UNAUTHORIZED_SERVICE_INVOKER = 401
    VALIDATION_FAIL = 400
    BAD_PARAMETER = 400
    UNAUTHORIZED = 401
    NOT_INITIALIZED = 400
    USER_NOT_LOGIN = 401
    RPC_FAIL = 400
    NOT_FOUND = 404

def get_message_by_httpstatus_code(code):
    key = ''
    for _v in APIResponseHTTPCode:
        if _v.value == code.value:
            key = _v.name
            break
    message = ''
    for _v in APIResponseMessage:
        if _v.name == key:
            message = _v.value
            break
    code = ''
    for _v in APIResponse:
        if _v.name == key:
            code = _v.value
            break

    return code,message

def create_response(status_code,data=None):
    code, message = get_message_by_httpstatus_code(status_code)
    _data = {}
    _data['code'] = code
    _data['message'] = message
    if data:
        _data['data'] = data
    return Response(data, status=status_code.value)

def create_data(status_code,data=None):
    code, message = get_message_by_httpstatus_code(status_code)
    _data = {}
    _data['code'] = code
    _data['message'] = message
    if data != None:
        _data['data'] = data
    return _data


class Response(SimpleTemplateResponse):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.

        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)
        from rest_framework import status as status_code

        if (isinstance(data,dict)):
            _keys = data.keys()
            if 'code' in _keys and 'message' in _keys:
                self.data = data
            else:
                self.data = create_data(APIResponseHTTPCode.SUCCESS, data)
        elif (status == None) or (status < status_code.HTTP_400_BAD_REQUEST):
            self.data = create_data(APIResponseHTTPCode.SUCCESS,data)
        elif (status == status_code.HTTP_404_NOT_FOUND):
            self.data = create_data(APIResponseHTTPCode.NOT_FOUND)
        else:
            self.data = create_data(APIResponseHTTPCode.FAIL,data)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value

    @property
    def rendered_content(self):
        renderer = getattr(self, 'accepted_renderer', None)
        accepted_media_type = getattr(self, 'accepted_media_type', None)
        context = getattr(self, 'renderer_context', None)

        assert renderer, ".accepted_renderer not set on Response"
        assert accepted_media_type, ".accepted_media_type not set on Response"
        assert context is not None, ".renderer_context not set on Response"
        context['response'] = self

        media_type = renderer.media_type
        charset = renderer.charset
        content_type = self.content_type


        if content_type is None and charset is not None:
            content_type = "{0}; charset={1}".format(media_type, charset)
        elif content_type is None:
            content_type = media_type
        self['Content-Type'] = content_type

        sysstr = platform.system()
        if sysstr.lower() == 'windows':
            ret = renderer.render(self.data, accepted_media_type, context)
        else:
            if content_type == 'application/openapi+json':
                ret = renderer.render(self.data['data'], accepted_media_type, context)

            elif content_type.find('json') > -1:
                ret = renderer.render(self.data, accepted_media_type, context)
            else:
                ret = renderer.render(self.data['data'], accepted_media_type, context)

        if isinstance(ret, six.text_type):
            assert charset, (
                'renderer returned unicode, and did not specify '
                'a charset value.'
            )
            return bytes(ret.encode(charset))

        if not ret:
            del self['Content-Type']

        return ret

    @property
    def status_text(self):
        """
        Returns reason text corresponding to our HTTP response status code.
        Provided for convenience.
        """
        return responses.get(self.status_code, '')

    def __getstate__(self):
        """
        Remove attributes from the response that shouldn't be cached.
        """
        state = super(Response, self).__getstate__()
        for key in (
            'accepted_renderer', 'renderer_context', 'resolver_match',
            'client', 'request', 'json', 'wsgi_request'
        ):
            if key in state:
                del state[key]
        state['_closable_objects'] = []
        return state