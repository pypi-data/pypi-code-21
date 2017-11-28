import time

class Tracker(object):

    def __init__(self,request):
        self.request = request
        self.create_tracker(request)

    def create_tracker_id(self):
        return int(time.time())

    def create_tracker(self,request):
        attributes = {}
        attributes['isBusinessError'] = False
        attributes['cloudServiceFromIndex'] = "10300"
        attributes['method'] = request.method.lower()
        attributes['operationCode'] = ''
        attributes['error'] = 'API执行成功'
        attributes['responseCode'] = 'success'
        attributes['applicationIndex'] = '10300'
        attributes['requestBytesRead'] = -1
        attributes['application'] = 'python-sweet'
        attributes['responseBytesWrite'] = 10000
        attributes['cloudServiceFrom'] = 'python-sweet'
        attributes['host'] = '127.0.0.1'
        attributes['operation'] = '查询消息'
        attributes['status'] = 200
        attributes['uri'] = request.path
        attributes['remote'] = request.META['REMOTE_ADDR']
        attributes['type'] = 'HTTP'

        tracker = {}
        tracker['appName'] = ''
        tracker['appId'] = ''
        tracker['appVersion'] = ''
        tracker['host'] = ''
        tracker['logTime'] = int(time.time())
        tracker['pid'] = 0
        tracker['projectId'] = None
        tracker['traceId'] = "gpmp-10300-17112109412448994229978112-|1-2-1|:2"  # 应用名-实例-时间戳+唯一id-|跨进程或线程调用步长|:兼容老版本步长
        tracker['cost'] = '1.83ms'
        tracker['startTimeStr'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        tracker['attributes'] = attributes
        tracker['processes'] = []
        tracker['parametersJson'] = {}
        tracker['errorStack'] = None
        self.tracker = tracker


    def create_processes(self,request):
        processes = {}
        processes['name'] = request.path #/tenant/0->TenantInfoServiceImpl.getTenantInfo()
        processes['cost'] = '1.2ms'
        processes['attributes'] = {}
        processes['type'] = 'Controller'  #Service  DataAccess

    def print_exec_time(self):
        print( str(time.time() - self.tracker['logTime']))