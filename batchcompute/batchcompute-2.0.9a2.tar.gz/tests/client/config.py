import os
import ConfigParser

from batchcompute import CN_QINGDAO as REGION
# Your access_id and secret_key pair
ID = ''
KEY = ''
ENDPOINT = ''
REGION_NAME = 'cn-qingdao'
 
OSS_HOST = ''
OSS_BUCKET = ''

LINUX_IMAGE_ID = ''
WINDOWS_IMAGE_ID = ''


# Try to get config from config file.
CONFIG_FILE_NAME = '/home/admin/.pythonsdk.ini'

if os.path.exists(CONFIG_FILE_NAME):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE_NAME)
else:
    config = {}

ID = ID or config.get('service', 'bcs_access_id')
KEY = KEY or config.get('service', 'bcs_access_key')
ENDPOINT = ENDPOINT or config.get('service', 'endpoint')
REGION_NAME = REGION_NAME or config.get('service', 'region')

OSS_HOST = OSS_HOST or config.get('oss', 'host')
OSS_BUCKET = OSS_BUCKET or config.get('oss', 'bucket')

LINUX_IMAGE_ID = LINUX_IMAGE_ID or config.get('image', 'linux')
WINDOWS_IMAGE_ID = WINDOWS_IMAGE_ID or config.get('image', 'windows')

# Write back confgis to config file.
config_back = ConfigParser.RawConfigParser()

config_back.add_section('service')
config_back.set('service', 'endpoint', ENDPOINT)
config_back.set('service', 'region', REGION_NAME)
config_back.set('service', 'bcs_access_id', ID)
config_back.set('service', 'bcs_access_key', KEY)

config_back.add_section('image')
config_back.set('image', 'linux', LINUX_IMAGE_ID)
config_back.set('image', 'windows', WINDOWS_IMAGE_ID)

config_back.add_section('oss')
config_back.set('oss', 'host', OSS_HOST)
config_back.set('oss', 'bucket', OSS_BUCKET)
config_back.set('oss', 'oxs_access_id', ID)
config_back.set('oss', 'oxs_access_key', KEY)

config_file = open(CONFIG_FILE_NAME, 'wb')
config_back.write(config_file)
config_file.close()

PATH_TMPL = 'oss://%s/%s'

PACKAGE_PATH = 'batchcompute_python_sdk/package/worker.tar.gz'
# FULL_PACKAGE = PATH_TMPL%(OSS_BUCKET, PACKAGE_PATH)
FULL_PACKAGE = PATH_TMPL%(OSS_BUCKET, PACKAGE_PATH)

DATA_PATH = 'batchcompute_python_sdk/data/'
FULL_DATA = PATH_TMPL%(OSS_BUCKET, DATA_PATH)
LOCAL_DATA = '/home/admin/batch_python_sdk/'

OUTPUT_PATH = 'batchcompute_python_sdk/output/find_task_result.txt'
FULL_OUTPUT = PATH_TMPL%(OSS_BUCKET, OUTPUT_PATH)

LOG_PATH = 'oss://%s/batchcompute_python_sdk/logs/'%OSS_BUCKET

print ID, KEY, ENDPOINT, OSS_HOST, OSS_BUCKET, LINUX_IMAGE_ID, WINDOWS_IMAGE_ID
