from rest_framework.response import Response
from rest_framework.views import APIView

from SweetPy.extend.response_plus import create_response, APIResponseHTTPCode
from SweetPy.setting import sweet_settings


class touch(APIView):
    def get(self, request, format=None):
        """
        应用活动检测
        """
        return Response(True)
class metrics(APIView):
    def get(self, request, format=None):
        """
        获取应用统计指标
        """
        return Response({})
class logger_query(APIView):
    def get(self, request,format=None):
        """
        查询日志配置
        """
        import logging
        v = request.GET.get('loggerName',None)
        if v == None:
            params_info = {}
            params_info['params'] = 'loggerName=xx'
            return create_response(APIResponseHTTPCode.BAD_PARAMETER,params_info)
        data = logging.getLevelName(logging.getLogger().level)
        return Response(data)

class errors_json(APIView):
    def get(self, request,format=None):
        """
        显示应用的错误码
        """
        data = {}
        from SweetPy.extend.response_plus import APIResponse,APIResponseMessage
        for _v in APIResponse:
            data[_v.value] = APIResponseMessage[_v.name].value
        return Response(data)

class configuration_namespaces(APIView):
    def get(self, request,format=None):
        """
        查询应用配置项命名空间
        """
        data = []
        data.append('SweetPy')
        data.append('SweetPy.setting')
        return Response(data)

class configuration_json(APIView):
    def get(self, request,format=None):
        """
        查询应用的配置参数
        """
        data = sweet_settings['applicationInstanceConfigurations']
        return Response(data)

class i18n_locale(APIView):
    def post(self, request,format=None):
        """
        改变后端响应消息的默认语言
        """
        locale = request.POST.get('localeString',None)
        cookie = str(request.POST.get('cookie',None)).lower() == 'true'
        if not locale or not cookie:
            params_info = {}
            params_info['params'] = 'localeString=xx&cookie=False'
            params_info['cookie'] = 'true false'
            params_info['localeString'] = 'zh en'
            return create_response(APIResponseHTTPCode.BAD_PARAMETER,params_info)
        _locale = locale.lower()
        if _locale.find('cn') != -1 or _locale.find('zh') != -1:
            sweet_settings['sweetpy.locale'] = 'CN'
        else:
            sweet_settings['sweetpy.locale'] = 'EN'

        return Response(True)

class logger_config(APIView):
    def post(self, request,format=None):
        """
        配置日志级别
        """
        loggerName = request.POST.get('loggerName',None)
        level = request.POST.get('level',None)
        if not loggerName or not level:
            params_info = {}
            params_info['params'] = 'loggerName=xx&level=DEBUG'
            params_info['level'] = 'DEBUG  INFO  WARN  ERROR  FATAL  OFF'
            return create_response(APIResponseHTTPCode.BAD_PARAMETER,params_info)
        import logging
        #TRACE  DEBUG  INFO  WARN  ERROR  FATAL  OFF
        # CRITICAL = 50
        # FATAL = CRITICAL
        # ERROR = 40
        # WARNING = 30
        # WARN = WARNING
        # INFO = 20
        # DEBUG = 10
        # NOTSET = 0
        if loggerName == 'DEBUG':
            level = logging.DEBUG
        elif loggerName == 'INFO':
            level = logging.INFO
        elif loggerName == 'WARN':
            level = logging.WARN
        elif loggerName == 'ERROR':
            level = logging.ERROR
        elif loggerName == 'FATAL':
            level = logging.FATAL
        elif loggerName == 'OFF':
            level = logging.NOTSET
        else:
            data = '不能识别的类型【' + loggerName + '】'
            return Response(data)
        logging.basicConfig(level=level)
        data = '日志级别已经切换到' + logging.getLevelName(level)
        return Response(data)


from django.conf.urls import RegexURLPattern
from django import conf
from django.conf import settings
from django.core.checks.urls import check_resolver
from django.core.checks.registry import register, Tags
conf.settings.INSTALLED_APPS.append('SweetPy.sweet_framework')

touch_regex =           RegexURLPattern('^sweet-framework/touch$', touch.as_view())
metrics_regex =         RegexURLPattern('^sweet-framework/metrics$', metrics.as_view())  #(?P<loggerName>[A-Za-z0-9]+)   \?loggerName=(?P<loggerName>[A-Za-z0-9]+)
logger_query_regex =    RegexURLPattern('^sweet-framework/logger/query$', logger_query.as_view())
errors_json_regex =     RegexURLPattern('^sweet-framework/errors/json$', errors_json.as_view())
configuration_namespaces_regex = RegexURLPattern('^sweet-framework/configuration/namespaces$', configuration_namespaces.as_view())
configuration_json_regex =       RegexURLPattern('^sweet-framework/configuration/json$', configuration_json.as_view())
i18n_locale_regex =              RegexURLPattern('^sweet-framework/i18n/locale$', i18n_locale.as_view())
logger_config_regex =            RegexURLPattern('^sweet-framework/logger/config$', logger_config.as_view())
@register(Tags.urls)
def check_url_config(app_configs, **kwargs):
    if getattr(settings, 'ROOT_URLCONF', None):
        from django.urls import get_resolver
        resolver = get_resolver()
        global sweet_regex
        resolver.url_patterns.append(touch_regex)
        resolver.url_patterns.append(metrics_regex)
        resolver.url_patterns.append(logger_query_regex)
        resolver.url_patterns.append(errors_json_regex)
        resolver.url_patterns.append(configuration_namespaces_regex)
        resolver.url_patterns.append(configuration_json_regex)
        resolver.url_patterns.append(i18n_locale_regex)
        resolver.url_patterns.append(logger_config_regex)
        return check_resolver(resolver)
    return []
import django
django.core.checks.urls.check_url_config = check_url_config