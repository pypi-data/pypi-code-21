# -*- coding: utf-8 -*-

NAME = 'batchcompute-cli'

COMMAND = 'batchcompute|bcs'
CMD = 'bcs'

LOCALE_SUPPORTED = ['en', 'zh', 'zh_CN']


VERSION = '1.5.6'

TEMPLATE_GATK_BUCKETS = {
'cn-beijing': 'genomics-public-data-beijing',
'cn-qingdao': 'genomics-public-data-qingdao',
'cn-shenzhen': 'genomics-public-data-shenzhen',
'cn-hangzhou': 'genomics-public-data-hangzhou',
'cn-shanghai': 'genomics-public-data-shanghai',
}


EVENTS = {
    'CLUSTER': [
        "OnClusterDeleted",
        "OnInstanceCreated",
        "OnInstanceActive"
    ],
    'JOB': [
        "OnJobWaiting",
        "OnJobRunning",
        "OnJobStopped",
        "OnJobFinished",
        "OnJobFailed",
        "OnTaskWaiting",
        "OnTaskRunning",
        "OnTaskStopped",
        "OnTaskFinished",
        "OnTaskFailed",
        "OnInstanceWaiting",
        "OnInstanceRunning",
        "OnInstanceStopped",
        "OnInstanceFinished",
        "OnInstanceFailed",
        "OnPriorityChange"
    ]
}

IT_MAP = {
"bcs.a2.large": {
    "cpu": 4,
    "memory": 8,
    "name": "bcs.a2.large",
    "disk": 400
  },
  "bcs.a2.xlarge": {
    "cpu": 8,
    "memory": 16,
    "name": "bcs.a2.xlarge",
    "disk": 400
  },
  "bcs.a2.3xlarge": {
    "cpu": 16,
    "memory": 32,
    "name": "bcs.a2.3xlarge",
    "disk": 400
  },
  "bcs.a2.4xlarge": {
    "cpu": 20,
    "memory": 40,
    "name": "bcs.a2.4xlarge",
    "disk": 400
  },
  "bcs.b4.4xlarge": {
    "cpu": 20,
    "memory": 80,
    "name": "bcs.b4.4xlarge",
    "disk": 1000
  },
  "bcs.b2.3xlarge": {
    "cpu": 16,
    "memory": 32,
    "name": "bcs.b2.3xlarge",
    "disk": 1000
  },
  "bcs.b4.xlarge": {
    "cpu": 8,
    "memory": 32,
    "name": "bcs.b4.xlarge",
    "disk": 1000
  },
  "bcs.b4.3xlarge": {
    "cpu": 16,
    "memory": 64,
    "name": "bcs.b4.3xlarge",
    "disk": 1000
  },
  "bcs.b4.5xlarge": {
    "cpu": 24,
    "memory": 96,
    "name": "bcs.b4.5xlarge",
    "disk": 1000
  }
}

from .util import config


configObj = config.getConfigs(config.COMMON)
region = configObj.get('region')
if region:
    REGION = region

IS_GOD = configObj.get('god') or False



import sys


# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
WIN = sys.platform == 'win32'

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode)
    NUMBER = (int, long)

if PY3:
    STRING = (str, bytes)
    NUMBER = int


# fix chinese view
def get_local():
    return codecs.lookup(locale.getpreferredencoding()).name
if PY2:
    import locale
    import codecs
    try:
        reload(sys)
        loc = get_local()
        sys.setdefaultencoding(loc) # utf-8
    except:
        pass



