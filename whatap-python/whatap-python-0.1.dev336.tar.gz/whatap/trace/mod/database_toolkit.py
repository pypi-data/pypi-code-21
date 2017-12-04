from whatap.trace import UdpSession, PacketTypeEnum
from whatap.trace.mod.application_wsgi import trace_handler
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context_manager import TraceContextManager


def instrument_sqlalchemy(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            ctx = TraceContextManager.getLocalContext()
            
            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            
            text = args[0].bind.url.__to_string__().replace('***', '')
            ctx.lctx['dbc'] = text
            
            datas = [' ', ' ', 'DB SESSION INFO: ' + text]
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)
            
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.Session.get_bind = wrapper(module.Session.get_bind)
