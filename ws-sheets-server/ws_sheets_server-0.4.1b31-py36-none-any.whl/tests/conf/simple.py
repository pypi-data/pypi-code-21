import enum
import os
import modconf

class Conf(object):
    @classmethod
    def _addr_storage(cls):
        if cls.kwargs.get('addr_storage', None):
            return cls.kwargs.get('addr_storage')

        if cls.DEV:
            return ('localhost',10001)

        return ('localhost',10002)

    @classmethod
    def _port(cls):
        if cls.kwargs.get('port', None):
            return cls.kwargs.get('port')

        if cls.DEV:
            return 10003

        return 10004

    @classmethod
    def prepare(cls, **kwargs):
        
        cls.DEV = kwargs.get('dev', False)

        cls.kwargs = kwargs

        cls.conf_sheets = modconf.import_conf('ws_sheets.tests.conf.simple')
        
        cls.STORAGE_HOST = 'localhost'
    
        cls.STORAGE_ADDR = cls._addr_storage()

        cls.PORT = cls._port()

        if cls.DEV:
            cls.LOG_DIR = '.dev/var/log/ws_sheets_server'
        else:
            cls.LOG_DIR = '/var/log/ws_sheets_server'

        LOG_FILE = os.path.join(cls.LOG_DIR, 'debug.log')
        LOG_FILE_CELL = os.path.join(cls.LOG_DIR, 'cell/debug.log')

        try:
            os.makedirs(os.path.dirname(LOG_FILE))
        except OSError as e: pass
        
        try:
            os.makedirs(os.path.dirname(LOG_FILE_CELL))
        except OSError as e: pass
       
        cls.LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {
                    'file': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename':LOG_FILE,
                        'formatter':'basic'
                        },
                    'file_cell': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename':LOG_FILE_CELL,
                        'formatter':'basic'
                        },
                    'console':{
                        'level':'DEBUG',
                        'class':'logging.StreamHandler',
                        'formatter': 'basic'
                        },
                    },
                'loggers':{
                    '__main__': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'async_patterns': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_storage': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets_server': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    'ws_sheets.cell/cell': {
                        'handlers': ['file_cell'],
                        'level': 'DEBUG',
                        'propagate': True,
                        },
                    },
                'formatters': {
                    "basic":{
                        "format":"%(asctime)s %(process)s %(module)10s %(funcName)20s %(levelname)7s %(message)s"
                        }
                    }
                }
        
        if cls.kwargs.get('console', False):
            cls.log_console()

    @classmethod
    def log_console(cls):
        for l in cls.LOGGING['loggers'].values():
            l['handlers'] = ['console']
  
  

  
  
