import arrow

from variables import ProjectName, SecretKey, DebugConfiguration, TripleDESToken
from variables import RedisConfiguration, KafkaConfiguration, JobConfiguration, AuthenticationConfiguration, DatabaseConfiguration, EncryptionConfiguration


class PrivateSetting(
                 ProjectName,
                 SecretKey,
                 
                 DebugConfiguration,

                 TripleDESToken,
                 
                 RedisConfiguration,
                 KafkaConfiguration,
                 
                 JobConfiguration,
                 AuthenticationConfiguration,
                 DatabaseConfiguration,
                 
                 EncryptionConfiguration,

                ):
    '''The goal of this class is to functionalize
    for better retrieval and defaults etc of 
    the various flavors that we want to allow...
    
    '''
    # basic things about the project!
    # these are typically django related! and very core
    _PROJECT_NAME = 'test'
    _SECRET_KEY = 'this must be filled'
    
    _DATABASE_SERVER = None
    
    # defines settings on messages
    _DEBUG = True
    _SHOW_DEBUG_TRACEBACK = True
    _SHOW_DEBUG_ERROR = False
    
    # encryption related and related to how the django_framework runs!
    _TRIPLE_DES_TOKEN_KEY = '0a405340000b493d8cf0' # this is used to encrypt your tokens so this really cant ever change!
    _TRIPLE_DES_TOKEN_IV = None # this is used to encrypt your tokens so this really cant ever change!
    
    # redis settings
    _REDIS_SERVER = None # if set, will also set REDIS_CACHE_ENABLED = True
    
    
    # kafka settings
    _KAFKA_SERVER = None # if set, will also set KAFKA_ENABLED = True
    
    # chai specific settings:
    _IS_AUTHENTICATION_SERVER = True  # flag is used to determine if this server is allowed to verify integrity of Token
    _AUTHENTICATION_SHOULD_PASSTHROUGH = True
    
    # chai sending jobs
    _ALLOW_SEND_JOBS = True
    _SEND_JOB_URL = 'https://redisapi.chaienergy.net/set_job/?format=json'
    _JOB_REPLY_URL = None # typically the same one as "as the server group url"
    
    
    _ENCRYPTION_SALT = None ## can be none

    #############################################
    #############################################
    # these we skip for now because they aren't too important
    ALLOWED_HOSTS = ['*']
    INTERNAL_IPS = ['127.0.0.1']

    # group names
    SERVER_GROUP = 'service' # nice to have settings
    SERVER_GROUP_URL = None # nice to have settings
    
    SERVER_NAME = 'service1' # nice to have settings
    SERVER_URL = 'localhost' # nice to have settings

    def __init__(self):
        
        self.initialize_time = arrow.utcnow()
        self.data = {}
    
    def _get_set_variables(self, var_name):
        value = self.get_variable(var_name = var_name)
        if not value:
            try:
                value, expire_at, ttl = getattr(self, '_get_' + var_name)()
                getattr(self, '_check_' + var_name)(value = value)
            except:
                print('variable: ', var_name)
                raise
            self.set_variable(var_name = var_name, value = value, expire_at = expire_at, ttl = ttl)

        return value
    
    def get_variable(self, var_name):
        
        value_dict = self.data.get('var_name')
        value = None
        if value_dict != None:
            if value_dict['ttl'] != None and (value_dict['set_at'].timestamp + value_dict['ttl'])  > arrow.utcnow().timestamp:
                value = None
            
            elif value_dict['expire_at'] > arrow.utcnow():
                value = None
            
            else:
                value = value_dict['value']

        return value
    
    def set_variable(self, var_name, value, expire_at = None, ttl = None):
        
        self.data[var_name] = {'set_at' : arrow.utcnow(), 'value' : value, 'expire_at' : expire_at, 'ttl' : ttl}
    
def main():
    ps = PrivateSetting()
    
    s  = ps.PROJECT_NAME
    
    print(s)

if __name__ == '__main__':
    main()
    