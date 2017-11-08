import threading
import uuid
import sys
from . import cache

TASK_STATUS_NEW = 'new'
TASK_STATUS_RUNNING = 'running'
TASK_STATUS_SUCC = 'succ'
TASK_STATUS_FAILED = 'failed'

class TaskWorker(threading.Thread):
    def __init__(self, taskItem):
        threading.Thread.__init__(self)
        self.taskItem = taskItem
    
    def run(self):
        taskResult = None
        if self.taskItem != None:
            # update status
            saveTaskResult(self.taskItem['id'], TASK_STATUS_RUNNING)
            try:
                taskResult = self.taskItem['function'](*self.taskItem['args'])
            except:
                saveTaskResult(self.taskItem['id'], TASK_STATUS_FAILED, err=str(sys.exc_info()))
            else:
                saveTaskResult(self.taskItem['id'], TASK_STATUS_SUCC, result=taskResult)

def submitTask(fn, *args):
    '''commit a task'''
    taskId = uuid.uuid1()
    taskItem = {'id':str(taskId), 'function':fn, 'args':args}
    saveTaskResult(taskItem['id'], TASK_STATUS_NEW)
    worker = TaskWorker(taskItem)
    worker.start()
    return taskItem['id']

def runTask(target, *args, **kwargs):
    worker = threading.Thread(group=None, target=target, args=args, kwargs=kwargs)
    worker.start()
    

def saveTaskResult(taskId, status, result=None, err=None):
    cacheKey = _buildCacheKey(taskId)
    taskResult = {'status':status, 'result':None, 'err':None}
    if result != None:
        taskResult['result'] = result
    if err != None:
        taskResult['err'] = err 
    cache.put(cacheKey, taskResult, 1200)

def queryTaskResult(taskId):
    cacheKey = _buildCacheKey(taskId)
    taskResult = cache.get(cacheKey)
    return taskResult

def _buildCacheKey(taskId):
    return '{}-{}'.format(__name__, taskId)
