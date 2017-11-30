import requests

'''
Sweet框架云模式接口
'''

base_url = None

def post_error_report(traceid,operation,operation_code,error):
    '''
    发送用户错误报告
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    params = {
        "traceId":traceid,
        "operation":operation,
        "operationCode": operation_code,
        "error": error
    }
    result = requests.post(base_url + 'framework/cloud/error-report',json=params)
    return result.text

def get_hystrix_metrics():
    '''
    查询所有Hystrix统计指标
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/cloud/hystrix/metrics')
    return result.text

def get_security_rules():
    '''
    服务调用安全规则
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/cloud/security-rules')
    return result.text

def get_service_list():
    '''
    查询服务路由表
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/cloud/service-list')
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
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    params = {
        "localeString":locale_string,
        "cookie":cookie
    }
    result = requests.post(base_url + 'framework/i18n/locale',json=params)
    return result.text

def post_logger_config(logger_name,level):
    '''
    配置日志级别
    :param logger_name:
    :param level: TRACE  DEBUG  INFO  WARN  ERROR  FATAL  OFF
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    params = {
        "loggerName":logger_name,
        "level":level
    }
    result = requests.post(base_url + 'framework/i18n/locale',json=params)
    return result.text

def get_configuration_json():
    '''
    查询应用的配置参数
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/configuration/json')
    return result.text

def get_configuration_namespaces():
    '''
    查询应用配置项命名空间
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/configuration/namespaces')
    return result.text

def get_errors_json():
    '''
    显示应用的错误码
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/errors/json')
    return result.text

def get_logger_query(logger_name):
    '''
    查询日志配置
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/logger/query?loggerName=' + logger_name)
    return result.text

def get_metrics():
    '''
    获取应用统计指标
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/metrics')
    return result.text

def get_touch():
    '''
    应用活动检测
    '''
    if not base_url:
        print('未获取到可用查询节点,查询失败!')
        return None
    result = requests.get(base_url + 'framework/touch')
    return result.text

if __name__ == '__main__':
    base_url = 'http://10.86.130.32:19250/'
    print( get_touch())
    print(get_errors_json())