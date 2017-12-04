from whatap.conf.configure import Configure as conf
from whatap.trace import UdpSession, PacketTypeEnum
from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor(fn, *args, **kwargs)
            
            return callback
        
        return trace
    
    module.WSGIHandler.__call__ = wrapper(module.WSGIHandler.__call__)


def instrument_handlers_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            request = args[1]
            ctx = TraceContextManager.getLocalContext()
            callback = fn(*args, **kwargs)
            
            if conf.trace_auto_normalize_enabled:
                resolver_match = request.resolver_match
                if resolver_match:
                    
                    path = request.path
                    for key, value in resolver_match.kwargs.items():
                        path = path.replace(resolver_match.kwargs[key],
                                            '{' + key + '}')
                    
                    start_time = DateUtil.nowSystem()
                    ctx.start_time = start_time
                    ctx.service_name = path
                    
                    if hasattr(resolver_match, 'view_name'):
                        type_name = 'View' \
                            if resolver_match._func_path != resolver_match.view_name \
                            else 'Function'
                        desc = '{0}: {1}'.format(type_name,
                                                 resolver_match._func_path)
                        datas = [' ', ' ', desc]
                        ctx.elapsed = DateUtil.nowSystem() - start_time
                        UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx,
                                               datas)
            
            return callback
        
        return trace
    
    module.BaseHandler.apply_response_fixes = wrapper(
        module.BaseHandler.apply_response_fixes)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            
            e = args[3]
            status_code = callback.status_code
            errors = [e[0].__name__,
                      e[1].args[1] if len(
                          e[1].args) > 1 \
                          else repr(e[1].args[0])]
            interceptor_error(status_code, errors)
            
            return callback
        
        return trace
    
    module.BaseHandler.handle_uncaught_exception = wrapper(
        module.BaseHandler.handle_uncaught_exception)


def instrument_generic_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            self = args[0]
            ctx = TraceContextManager.getLocalContext()
            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            desc = '{0}.{1}'.format(self.__module__, type(self).__name__)
            datas = [' ', ' ', desc]
            
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)
            
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.View.dispatch = wrapper(module.View.dispatch)


# Django==1.10

def instrument_urls_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.reverse = wrapper(module.reverse)


def instrument_handlers_exception(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.convert_exception_to_response.convert_exception_to_response = wrapper(
        module.convert_exception_to_response.convert_exception_to_response)
