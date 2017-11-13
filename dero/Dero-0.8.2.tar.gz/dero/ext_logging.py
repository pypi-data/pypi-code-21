
import datetime, os, sys
import logging, functools
import inspect
import timeit

from .ext_time import time_elapsed
from .decorators import apply_decorator_to_all_functions_in_module

def apply_logging_to_all_functions_in_module(module):
    """
    To be used after creating a logger with dero.logging.create_logger(), and after importing
    a module. On subsequent calls to any functions from that module, they will be logged using
    the log_with decorator. 
    
    NOTE: Be careful not to use this on any module containing a function to be called many times.
    For such modules, it is better to use the log_with decorator directly excluding those functions.
    
    Usage:
    import module
    import dero
    
    logger = dero.logging.create_logger()

    dero.logging.apply_logging_to_all_functions_in_module(module)
    
    module.whatever_function() #logs correctly
    
    """
    name = _get_all_prior_frames()
    name += '.' + module.__name__
    module.logger = logging.getLogger(name)
    module.log = log_with(module.logger)
    apply_decorator_to_all_functions_in_module(module, module.log)

def create_logger(name='main'):
    """
    Creates a logger in the __main__ namespace. Sets three handlers, two to file and one to stdout.
    All output goes to the .debug file, info and higher goes to the .log file, and error and higher
    goes to stdout.
    
    Pass a name to name log files.
    
    Usage:
    Imagine a project with three files, main.py, bar.py, and baz.py. We want to use the 
    create_logger() function in the main namespace (file being run), and get_logger() in
    the imported files.
    
    Normal logs:
    Then log entries may be created with logger.debug(), logger.info(), logger.warning(), logger.error(),
    and logger.critical(). 
    
    Exceptions:
    Log caught exceptions with logger.exception('Custom message'), this will include the traceback
    
    Entering and exiting functions:
    Use @dero.logging.log_with(logger) decorator, logs when entering and exiting function as well as
    passed args and kwargs and return values. Logs enter and exit at the info level and parameters and
    return values at the debug level.
    
    Example usage:
    main.py:
    import dero
    
    logger = dero.logging.create_logger()

    logger.info('Starting main')
    bar.barf()
    
    bar.py:
    import dero
    import baz
    
    logger = dero.logging.get_logger()
    
    def barf():
        logger.info('some info about barf')
        baz.baz()
        
    baz.py:
    import dero
    
    logger = dero.logging.get_logger()
    
    def baz():
        logger.info('some info about baz')
        
    Running main.py will output:
    2016-08-08 15:09:17,109 - __main__ - INFO - Starting main
    2016-08-08 15:09:17,111 - __main__.bar - INFO - some info about barf
    2016-08-08 15:09:17,111 - __main__.bar.baz - INFO - some info about baz

    """
    #Clear Jupyter notebook logger (this is code that only needs to be run in jupyter notebook)
    logger = logging.getLogger()
    logger.handlers = []

    #Create logger
    logger = logging.getLogger('__main__')
    logger.setLevel(logging.DEBUG)

    handlers = [] #container for handlers
    
    #Make log dir
    if not os.path.exists('Logs'): os.makedirs('Logs')

    #Create debug logfile which logs everything
    creation_time = str(datetime.datetime.now().replace(microsecond=0)).replace(':','.')
    debug_handler = logging.FileHandler(r'Logs\{} {}.debug'.format(creation_time, name))
    debug_handler.setLevel(logging.DEBUG)
    handlers.append(debug_handler)

    #Create standard logfile which logs process (info and up)
    info_handler = logging.FileHandler(r'Logs\{} {}.log'.format(creation_time, name))
    info_handler.setLevel(logging.INFO)
    handlers.append(info_handler)

    #Now log errors to standard output
    error_handler = logging.StreamHandler(sys.stdout)
    error_handler.setLevel(logging.ERROR)
    handlers.append(error_handler)

    formatter = logging.Formatter('%(asctime)ls - %(name)s - %(levelname)s - %(message)s')

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def get_logger():
    """
    To be used in an imported file. See create_logger() for usage.
    """
    name = _get_all_prior_frames()
    return logging.getLogger(name)

def _get_all_prior_frames():
    """
    Gets the calling stack formatted as a string seperated by periods, e.g.:
    __main__.bar.baz
    """
    frame = inspect.currentframe()
    out = [] #container for output
    while True:
        frame = frame.f_back
        name = _filter_frame(frame)
        if frame is not None:
            if name is not False: #if False, is a name we don't need to record, should just continue
                out = [name] + out
                if name == '__main__': #once we get to __main__, we're done (ignore IPython stuff)
                    return '.'.join(out)
        else: #if frame is none, we're done (no more frames)
            return '.'.join(out)

def _filter_frame(frame):
    """
    Checks if this frame is something meaningful and takes the appropriate action
    
    Returns the name if valid name, returns False if invalid name, returns None if frame is None
    """
    try: name = frame.f_globals['__name__']
    except AttributeError: #frame is None
        return None
    if name in ('importlib._bootstrap','importlib._bootstrap_external', __name__):
        return False
    return name

def get_func_signature(func):
    code_list = inspect.getsourcelines(func)[0]
    code_str = ' '.join([c.strip() for c in code_list])
    return code_str[code_str.find('def') + 4:code_str.find(':')]

class log_with(object):
    '''Logging decorator that allows you to log with a
    specific logger.
    
    By default, logs entering and exiting function as well as arguments passed at the info level.
    
    Usage:
    import logging
    import dero
    
    logging.basicConfig()
    log = logging.getLogger('__name__') #can use custom name but using module name comes with benefits
    log.setLevel(logging.DEBUG)

    @dero.logging.log_with(log)
    def test_func(a, b, c=5):
        return a + b
    '''
    # Customize these messages
    ENTRY_MESSAGE = 'Entering {}'
    args_message = 'Passed Args: \n{}, Kwargs: {}'
    result_message = '{} Result: \n{}'
    time_message = '{} took {}'
    EXIT_MESSAGE = 'Exiting {}'

    def __init__(self, logger=None, timer=True):
        self.logger = logger
        self.timer = timer

    def __call__(self, func):
        '''Returns a wrapper that wraps func.
The wrapper will log the entry and exit points of the function
with logging.INFO level.
'''
        # set logger if it was not set earlier
        if not self.logger:
            logging.basicConfig()
            self.logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            if self.timer:
                start_time = timeit.default_timer()
            
            
            self.logger.info(self.ENTRY_MESSAGE.format(get_func_signature(func)))  # logging level .info(). Set to .debug() if you want to
            self.logger.debug(self.args_message.format(args, kwds))
            f_result = func(*args, **kwds)
            self.logger.debug(self.result_message.format(func.__name__, f_result))
            time_elapsed_str = time_elapsed(timeit.default_timer() - start_time)
            self.logger.debug(self.time_message.format(func.__name__, time_elapsed_str))
            self.logger.info(self.EXIT_MESSAGE.format(func.__name__))   # logging level .info(). Set to .debug() if you want to
            return f_result
        return wrapper

class Logger:
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        
        self.log_list = []
        self.create_log_file()

    def log(self, message, error=False, neverprint=False):
        if error:
            message = 'ERROR: ' + message
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        if self.debug and not neverprint:
            sys.stdout.write(message + '\n')
            sys.stdout.flush() #forces output now
        try:
            with open(self.log_path, 'a') as f:
                [f.write(item) for item in self.log_list] #log anything saved in memory that couldn't be written before
                f.write(message)
                f.write('\n')
            self.log_list = []
        except PermissionError: #if someone happened to write to the file at the same time
            self.log_list.append(message) #save it to log later
            self.log_list.append('\n')

    def create_log_file(self):
        name = 'log_' + str(datetime.datetime.now().replace(microsecond=0)).replace(':','.') + '.txt'
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)
        self.log_path = os.path.join(self.log_dir, name)

        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write('\n')


        