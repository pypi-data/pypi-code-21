from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_db_con, interceptor_db_execute, interceptor_db_close


def instrument_MySQLdb(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            db_type = 'mysql'
            callback = interceptor_db_con(fn, db_type, *args, **kwargs)
            return callback
        
        return trace
    
    module.connect = wrapper(module.connect)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback
        
        return trace
    
    get_dict(module.connection)['close'] = wrapper(
        module.connection.close)


def instrument_MySQLdb_cursors(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_execute(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.BaseCursor.execute = wrapper(module.BaseCursor.execute)


def instrument_pymysql(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            db_type = 'mysql'
            callback = interceptor_db_con(fn, db_type, *args, **kwargs)
            return callback
        
        return trace
    
    module.connect = wrapper(module.connect)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.connections.Connection.close = wrapper(
        module.connections.Connection.close)
