import requests

'''
Sweet框架云模式接口
'''

base_url = 'http://10.86.130.32:19250/'

def post_error_report(traceid,operation,operation_code,error):
    '''
    发送用户错误报告
    '''
    params = {
        "traceId":traceid,
        "operation":operation,
        "operationCode": operation_code,
        "error": error
    }
    result = requests.post(base_url + 'sweet-framework/cloud/error-report',json=params)
    return result.text

def get_hystrix_metrics():
    '''
    查询所有Hystrix统计指标
    '''
    result = requests.get(base_url + 'sweet-framework/cloud/hystrix/metrics')
    return result.text

def get_security_rules():
    '''
    服务调用安全规则
    '''
    result = requests.get(base_url + 'sweet-framework/cloud/security-rules')
    return result.text

def get_service_list():
    '''
    查询服务路由表
    '''
    result = requests.get(base_url + 'sweet-framework/cloud/service-list')
    return result.text


'''
Sweet框架接口
'''

def post_i18n_locale(locale_string,cookie):
    '''
    改变后端响应消息的默认语言
    :param locale_string:
    :param cookie:
    '''
    params = {
        "localeString":locale_string,
        "cookie":cookie
    }
    result = requests.post(base_url + 'sweet-framework/i18n/locale',json=params)
    return result.text

def post_logger_config(logger_name,level):
    '''
    配置日志级别
    :param logger_name:
    :param level: TRACE  DEBUG  INFO  WARN  ERROR  FATAL  OFF
    '''
    params = {
        "loggerName":logger_name,
        "level":level
    }
    result = requests.post(base_url + 'sweet-framework/i18n/locale',json=params)
    return result.text

def get_configuration_json():
    '''
    查询应用的配置参数
    '''
    result = requests.get(base_url + 'sweet-framework/configuration/json')
    return result.text

def get_configuration_namespaces():
    '''
    查询应用配置项命名空间
    '''
    result = requests.get(base_url + 'sweet-framework/configuration/namespaces')
    return result.text

def get_errors_json():
    '''
    显示应用的错误码
    '''
    result = requests.get(base_url + 'sweet-framework/errors/json')
    return result.text

def get_logger_query(logger_name):
    '''
    查询日志配置
    '''
    result = requests.get(base_url + 'sweet-framework/logger/query?loggerName=' + logger_name)
    return result.text

def get_metrics():
    '''
    获取应用统计指标
    '''
    result = requests.get(base_url + 'sweet-framework/metrics')
    return result.text

def get_touch():
    '''
    应用活动检测
    '''
    result = requests.get(base_url + 'sweet-framework/touch')
    return result.text