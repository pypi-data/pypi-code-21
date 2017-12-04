from rest_framework.response import Response
from rest_framework.views import APIView

from SweetPy.extend.response_plus import create_response, APIResponseHTTPCode


class cloud_hystrix_metrics(APIView):
    def get(self, request, format=None):
        """
        查询所有Hystrix统计指标
        """
        data = {}
        data['threadPoolMetrics'] = []
        data['commandMetrics'] = []
        data['collapserMetricses'] = []
        return Response(data)
class cloud_security_rules(APIView):
    def get(self, request, format=None):
        '''
        服务调用安全规则
        '''
        data = {}
        data['defaultPolicy'] = 'ACCEPT'
        data['rules'] = []
        return Response(data)
class cloud_service_list(APIView):
    def get(self, request, format=None):
        '''
        服务调用安全规则
        '''
        data = {}
        data['service-list'] = {}
        from SweetPy.setting import zk_plus,get_local_ip,sweet_py_version
        app_name = settings.SWEET_CLOUD_APPNAME
        app_host = get_local_ip()
        app_port = settings.SWEET_CLOUD_APPPORT
        app_version = settings.SWEET_CLOUD_VERSION
        zk_info = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, sweet_py_version,
                                                        state='Running')
        data['service-list'][app_name] = zk_info
        return Response(data)

class cloud_error_report(APIView):
    def post(self, request, format=None):
        '''
        发送用户错误报告
        '''
        traceId = request.GET.get('traceId', None)
        operation = request.GET.get('operation', None)
        operationCode = request.GET.get('operationCode', None)
        error = request.GET.get('error', None)

        if not traceId or not operation or not operationCode or not error:
            params_info = {}
            params_info['params'] = 'traceId=XX&operation=XX&operationCode=XX&error=XX'
            return create_response(APIResponseHTTPCode.BAD_PARAMETER, params_info)
        return create_response(APIResponseHTTPCode.FAIL)

from django.conf.urls import RegexURLPattern
from django import conf
from django.conf import settings
from django.core.checks.urls import check_resolver
from django.core.checks.registry import register, Tags
conf.settings.INSTALLED_APPS.append('SweetPy.sweet_framework_cloud')

cloud_hystrix_metrics_regex = RegexURLPattern('^sweet-framework/cloud/hystrix/metrics$', cloud_hystrix_metrics.as_view())
cloud_security_rules_regex = RegexURLPattern('^sweet-framework/cloud/security-rules$', cloud_security_rules.as_view())
cloud_service_list_regex = RegexURLPattern('^sweet-framework/cloud/service-list$', cloud_service_list.as_view())
cloud_error_report_regex = RegexURLPattern('^sweet-framework/cloud/error-report$', cloud_error_report.as_view())
@register(Tags.urls)
def check_url_config(app_configs, **kwargs):
    if getattr(settings, 'ROOT_URLCONF', None):
        from django.urls import get_resolver
        resolver = get_resolver()
        resolver.url_patterns.append(cloud_hystrix_metrics_regex)
        resolver.url_patterns.append(cloud_security_rules_regex)
        resolver.url_patterns.append(cloud_service_list_regex)
        resolver.url_patterns.append(cloud_error_report_regex)
        return check_resolver(resolver)
    return []
import django
django.core.checks.urls.check_url_config = check_url_config