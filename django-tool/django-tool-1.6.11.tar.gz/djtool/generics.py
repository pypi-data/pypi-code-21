from rest_framework import generics
from rest_framework.views import APIView
from django.http.response import HttpResponseBase
from rest_framework.response import Response
from django.utils.cache import cc_delim_re, patch_vary_headers
from rest_framework import exceptions, status
from djtool import Common
import json


class APIView(APIView):
    pass


class GenericAPIView(generics.GenericAPIView, APIView, Common):

    transform_code = {
        '404': '50005',
        '403': '50000',
        '200': '20000',
        '201': '20000',
    }

    def _validate_code(self, request, code):
        if isinstance(self.code, (str, int)):
            return self.code
        elif isinstance(self.code, dict):
            method = request.method.lower()
            if method in self.code:
                return self.code[method]
            else:
                raise Exception('请配置响应码（code）')
        else:
            raise Exception('配置响应码（code）格式错误')

    def _code(self, request, response, key='code'):
        if hasattr(self, key):
            return self._validate_code(request, getattr(self, key))
        elif hasattr(request, key):
            return self._validate_code(request, getattr(request, key))
        else:
            return self._transform(str(response.status_code))

    def _transform(self, status):
        try:
            return self.transform_code[status]
        except:
            raise Exception('请配置transform_code')

    def factory_response(self, request, response, *args, **kwargs):
        if 'code' not in response.data or 'msg' not in response.data:
            if response.exception:
                response.data = self.msg(self._code(request, response, key="code_fail"))
            else:
                response.data = self.msg(self._code(request, response), response.data)
        if isinstance(response.data, dict):
            response.data = json.dumps(response.data, ensure_ascii=False)
        return response

    def finalize_response(self, request, response, *args, **kwargs):
        assert isinstance(response, HttpResponseBase), (
            'Expected a `Response`, `HttpResponse` or `HttpStreamingResponse` '
            'to be returned from the view, but received a `%s`'
            % type(response)
        )

        if isinstance(response, Response):
            if not getattr(request, 'accepted_renderer', None):
                neg = self.perform_content_negotiation(request, force=True)
                request.accepted_renderer, request.accepted_media_type = neg

            response.accepted_renderer = request.accepted_renderer
            response.accepted_media_type = request.accepted_media_type
            response.renderer_context = self.get_renderer_context()

        vary_headers = self.headers.pop('Vary', None)
        if vary_headers is not None:
            patch_vary_headers(response, cc_delim_re.split(vary_headers))

        for key, value in self.headers.items():
            response[key] = value

        response = self.factory_response(request, response, *args, **kwargs)

        return response

    def handle_exception(self, exc):
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        exception_handler = self.get_exception_handler()

        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)

        if response is None:
            self.raise_uncaught_exception(exc)

        response.exception = True
        return response


class ListAPIView(GenericAPIView, generics.ListAPIView):
    pass


class CreateAPIView(GenericAPIView, generics.CreateAPIView):
    pass


class RetrieveAPIView(GenericAPIView, generics.RetrieveAPIView):
    pass
