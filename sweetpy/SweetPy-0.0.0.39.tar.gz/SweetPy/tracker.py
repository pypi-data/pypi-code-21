import time
from django.conf import settings
from .time_plus import DatetimePlus
from .setting import sweet_settings
from .func_plus import FuncHelper
from .extend.rabbitmq_plus import Producer
from .extend.response_plus import get_message_by_httpstatus_code,APIResponseHTTPCode

def get_local_ip():
    import socket
    localIP = socket.gethostbyname(socket.gethostname())
    return localIP

producer = None

class Tracker(object):

    def __init__(self,request):
        self.start_time = time.time()
        self.request = request
        self.layer_cur = 0
        self.layer_str = ''
        self.create_tracker(request)

    def create_tracker_id(self):
        result = settings.SWEET_CLOUD_APPNAME + '-' + \
            str(settings.SWEET_CLOUD_APPPORT) + '-' + \
            str(DatetimePlus.get_time_stamp_millisecond()) +\
            FuncHelper.get_random_str(13,only_num=True)
        #'17112109412448994229978112'
        result += '-|1|:1'
        return result

    def create_tracker(self,request):
        attributes = {}
        attributes['isBusinessError'] = False
        attributes['cloudServiceFromIndex'] = str(settings.SWEET_CLOUD_APPPORT)
        attributes['method'] = request.method.lower()
        attributes['operationCode'] = ''
        attributes['error'] = 'API执行成功1'
        attributes['responseCode'] = 'success1'
        attributes['applicationIndex'] = str(settings.SWEET_CLOUD_APPPORT)
        attributes['requestBytesRead'] = -1
        attributes['application'] = settings.SWEET_CLOUD_APPNAME
        attributes['responseBytesWrite'] = settings.SWEET_CLOUD_APPPORT
        attributes['cloudServiceFrom'] = settings.SWEET_CLOUD_APPNAME
        attributes['host'] = get_local_ip()
        attributes['operation'] = ''
        attributes['status'] = 200
        attributes['uri'] = request.path
        attributes['remote'] = request.META['REMOTE_ADDR']
        attributes['type'] = 'HTTP'

        tracker = {}
        tracker['appName'] = settings.SWEET_CLOUD_APPNAME
        tracker['appId'] = str(settings.SWEET_CLOUD_APPPORT)
        tracker['appVersion'] = settings.SWEET_CLOUD_VERSION
        tracker['host'] = get_local_ip()
        tracker['logTime'] = DatetimePlus.get_time_stamp_millisecond()
        tracker['pid'] = 0
        tracker['projectId'] = None
        tracker['traceId'] = self.create_tracker_id()

        #"gpmp-10300-17112109412448994229978112-|1-2-1|:2"
        # 应用名-实例-时间戳+唯一id-|跨进程或线程调用步长|:兼容老版本步长
        tracker['cost'] = ''
        tracker['startTimeStr'] = DatetimePlus.get_nowdatetime_to_str()
        tracker['attributes'] = attributes
        tracker['processes'] = []
        tracker['parametersJson'] = {}
        tracker['errorStack'] = None
        self.tracker = tracker

    def set_attributes_operation(self,operation):
        self.tracker['attributes']['operation'] = operation

    def set_attributes_status(self,status):
        self.tracker['attributes']['status'] = status

    def set_cost(self):
        self.tracker['cost'] = '{0:.2f}ms'.format(time.time() - self.start_time)

    def create_processes(self,path,cost,attributes,type):
        if self.layer_cur < 1:
            self.layer_cur = 1
            self.layer_str = '1'
        else:
            self.layer_cur = 2
            self.layer_str += '-' + str(self.layer_cur) + '-1'
        processes = {}
        processes['name'] = path #/tenant/0->TenantInfoServiceImpl.getTenantInfo()
        processes['cost'] = '{0:.2f}ms'.format(cost)
        processes['attributes'] = attributes
        processes['type'] = type  #Service  DataAccess  Controller
        self.tracker['processes'].append(processes)

    def send_to_mq(self):
        if not sweet_settings.get('mqLogEnabled',False):
            return
        connectionString = sweet_settings['mq']['connectionString']
        user = sweet_settings['mq']['user']
        password = sweet_settings['mq']['password']
        traceLogQueueName = sweet_settings['mq']['traceLogQueueName']
        # apmLogQueueName = sweet_settings['apmLogQueueName']['apmLogQueueName']

        global producer
        if not producer:
            producer = Producer(connectionString,user,password,traceLogQueueName)
        jsondata = FuncHelper.dict_to_json(self.tracker)
        result = producer.send(jsondata)
        return result
        # if result:
        #     print('send mq data success')
        # else:
        #     print('send mq data failed')

    def end(self):
        self.set_cost()
        self.set_end_state()
        self.send_to_mq()

    def set_end_state(self):
        self.tracker['attributes']['error'], self.tracker['attributes'][
            'responseCode'] = get_message_by_httpstatus_code(APIResponseHTTPCode.SUCCESS)

    def end_by_exection(self,exection):
        self.set_cost()
        self.set_excetion(exection)
        self.send_to_mq()

    def set_excetion(self,exection):
        self.tracker['attributes']['error'], self.tracker['attributes']['responseCode'] = get_message_by_httpstatus_code(APIResponseHTTPCode.FAIL)
        self.tracker['errorStack'] = str(exection)
        self.tracker['attributes']['status'] = APIResponseHTTPCode.FAIL.value

    def add_layer(self,func_name,cost_time,attributes,type):
        func_name = self.tracker['attributes']['method'] + '->' + func_name
        self.create_processes(self,func_name,cost_time,attributes,type)

    def print_exec_time(self):
        self.set_cost()
        print(self.tracker['cost'])
        print(self.tracker)