'''Constants used across the BatchCompute SDK package in general.
'''
import sys
import logging
from datetime import datetime

# A dictionary to map numeric state to string state.
STATE_MAP = [
    'Init', 'Waiting', 'Running',
    'Finished', 'Failed', 'Stopped'
]

# BatchCompute endpoint information.
ENDPOINT_INFO = {
    'cn-qingdao': 'batchcompute.cn-qingdao.aliyuncs.com',
    'cn-hangzhou': 'batchcompute.cn-hangzhou.aliyuncs.com',
    'cn-shenzhen': 'batchcompute.cn-shenzhen.aliyuncs.com',
    'cn-beijing': 'batchcompute.cn-beijing.aliyuncs.com',
}
SERVICE_PORT = 80 
SERVICE_PORT_MOCKED = 8888
SECURITY_SERVICE_PORT = 443
CN_HANGZHOU = ENDPOINT_INFO['cn-hangzhou']
CN_QINGDAO = ENDPOINT_INFO['cn-qingdao']
CN_SHENZHEN = ENDPOINT_INFO['cn-shenzhen']
CN_BEIJING = ENDPOINT_INFO['cn-beijing']

# Api version supported by BatchCompute.
API_VERSION = '2015-11-11'

# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY25 = sys.version_info[0] == 2 and sys.version_info[1] <= 5

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode, type(None), )
    NUMBER = (int, long, type(None), )

if PY3:
    STRING = (str, bytes, type(None), )
    NUMBER = (int, type(None), )

ANY = STRING + NUMBER
TIME = (int, datetime, type(None)) + STRING
COLLECTION = (list, tuple)

# Log configuration
LOG_LEVEL = logging.WARNING
LOG_FILE_NAME = 'batchcompute_python_sdk.LOG'
LOG_FORMATTER = "[%(asctime)s]\t[%(levelname)s]\t[%(thread)d]\t[%(pathname)s:%(lineno)d]\t%(message)s"
LOG_HANDLER = None
ALL_LOGS= {} 

# Default values
DEFAULT_LIST_ITEM = 100

# Time format
if PY25:
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
else:
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" 
