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
        self.tracker_id = Tracker.create_tracker_id()
        self.is_exection = False
        self.create_tracker(request)

    @staticmethod
    def create_tracker_id():
        return str(DatetimePlus.get_time_stamp_millisecond()) + \
                FuncHelper.get_random_str(13, only_num=True)

    def create_tracker(self,request):
        _form = request.META.get('X-SWEET-CLOUD-FROM', None)
        _form_index = request.META.get('X-SWEET-CLOUD-FROM-INDEX', None)
        _target = request.META.get('X-SWEET-CLOUD-TARGET', None)
        _target_version = request.META.get('X-SWEET-CLOUD-TARGET-VERSION', None)
        _target_id = request.META.get('X-SWEET-CLOUD-TRACE-ID', None)
        if _target_id is not None:
            self.tracker_id = _target_id

        attributes = {}
        attributes['isBusinessError'] = False
        if _form_index:
            attributes['cloudServiceFromIndex'] = _form_index
        else:
            attributes['cloudServiceFromIndex'] = ''
        attributes['method'] = request.method.lower()
        attributes['operationCode'] = ''
        attributes['error'] = 'API执行成功1'
        attributes['responseCode'] = 'success1'
        attributes['applicationIndex'] = str(settings.SWEET_CLOUD_APPPORT)
        attributes['requestBytesRead'] = -1
        attributes['application'] = settings.SWEET_CLOUD_APPNAME
        attributes['responseBytesWrite'] = settings.SWEET_CLOUD_APPPORT
        if _form:
            attributes['cloudServiceFrom'] = _form
        else:
            attributes['cloudServiceFrom'] = ''
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
        if self.layer_cur == 0:
            self.layer_cur = 1
            self.layer_str = '1'

        id = settings.SWEET_CLOUD_APPNAME + '-' + \
            str(settings.SWEET_CLOUD_APPPORT) + '-' + \
            self.tracker_id +  '-|' + self.layer_str + '|:' + str(self.layer_cur)
        self.tracker['traceId'] = id


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
        if sweet_settings is None:
            return
        if not sweet_settings.get('mqLogEnabled',False):
            return
        global producer
        if not producer:
            connectionString = sweet_settings['mq']['connectionString']
            user = sweet_settings['mq']['user']
            password = sweet_settings['mq']['password']
            traceLogQueueName = sweet_settings['mq']['traceLogQueueName']
            producer = Producer(connectionString,user,password,traceLogQueueName)
        jsondata = FuncHelper.dict_to_json(self.tracker)
        result = producer.send(jsondata)
        return result

    def end(self):
        self.set_cost()
        self.set_end_state()
        self.send_to_mq()


    def set_end_state(self):
        if self.is_exection is False:
            self.tracker['attributes']['error'], self.tracker['attributes'][
                'responseCode'] = get_message_by_httpstatus_code(APIResponseHTTPCode.SUCCESS)



    def set_excetion(self,exection):
        self.tracker['attributes']['error'], self.tracker['attributes']['responseCode'] = get_message_by_httpstatus_code(APIResponseHTTPCode.FAIL)
        self.tracker['errorStack'] = str(exection)
        self.tracker['attributes']['status'] = APIResponseHTTPCode.FAIL.value
        self.is_exection = True

    def add_layer(self,func_name,cost_time,attributes,type):
        func_name = self.tracker['attributes']['uri'] + '->' + func_name
        self.create_processes(func_name, cost_time, attributes, type)

