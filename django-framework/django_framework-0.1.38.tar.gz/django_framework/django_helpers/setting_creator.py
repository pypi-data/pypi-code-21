from django_framework.django_helpers.exception_helpers.try_except_response import SHOW_DEBUG_ERROR


class PrivateSetting(object):
    '''The goal of this class is to functionalize
    for better retrieval and defaults etc of 
    the various flavors that we want to allow...
    
    '''
    
    SHOW_DEBUG_ERROR = False
    
    
    SETTINGS_IV 
    SETTINGS_KEY
    
    
    PRIVATE_TRIPLE_DES_TOKEN_KEY = '0a405340000b493d8cf0' # this is used to encrypt your tokens so this really cant ever change!
    IS_AUTHENTICATION_SERVER = True  # flag is used to determine if this server is allowed to verify integrity of Token


    

PRIVATE_TRIPLE_DES_TOKEN_KEY = '0a405340000b493d8cf0' # this is used to encrypt your tokens so this really cant ever change!
IS_AUTHENTICATION_SERVER = True  # flag is used to determine if this server is allowed to verify integrity of Token

from kafka import KafkaProducer
import json
try:
    # kafka_connection = KafkaProducer(bootstrap_servers=['localhost:9092'])
    KAFKA_PRODUCER   = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda m: json.dumps(m).encode('ascii'))
    KAFKA_ENABLED = True
except:
    KAFKA_ENABLED = False
    


REDIS_CACHE_ENABLED = True
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


ALLOW_SEND_JOBS = True
SEND_JOB_URL = 'https://redisapi.chaienergy.net/set_job/?format=json'

SERVER_URL = 'localhost'
SERVER_GROUP = 'service'
SERVER_NAME = 'service1'