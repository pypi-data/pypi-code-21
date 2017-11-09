import traceback

from whatap.conf.configure import Configure as conf
from whatap.trace import UdpSession, PacketTypeEnum
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from functools import wraps
from whatap import logging
import re


def trace_handler(fn, start=False):
    def handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not start and not TraceContextManager.getLocalContext():
                return fn(*args, **kwargs)
            try:
                callback = func(*args, **kwargs)
            except Exception as e:
                logging.debug(e, extra={'id': 'WA917'}, exc_info=True)
                return fn(*args, **kwargs)
            else:
                return callback
        
        return wrapper
    
    return handler


def start_interceptor(service_name=None):
    ctx = TraceContext()
    
    if conf.dev:
        logging.debug('start transaction id(seq): {}'.format(ctx.id),
                      extra={'id': 'WA111'})
    
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    
    if service_name:
        ctx.service_name = service_name
        
        datas = [ctx.host,
                 ctx.service_name,
                 ctx.remoteIp,
                 ctx.userAgentString,
                 ctx.referer,
                 ctx.userid,
                 ctx.isStaticContents]
        
        UdpSession.send_packet(PacketTypeEnum.PACKET_REQUEST, ctx, datas)
    
    return ctx


def end_interceptor(thread_id=None):
    ctx = TraceContextManager.getContext(
        thread_id) if thread_id else TraceContextManager.getLocalContext()
    
    if conf.dev:
        logging.debug('end   transaction id(seq): {}'.format(ctx.id),
                      extra={'id': 'WA112'})
    
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    
    datas = [ctx.host, ctx.service_name]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    UdpSession.send_packet(PacketTypeEnum.PACKET_REQUEST_END, ctx,
                           datas)


def interceptor(rn_environ, *args, **kwargs):
    if not isinstance(rn_environ, tuple):
        rn_environ = (rn_environ, args[1])
    fn, environ = rn_environ
    
    ctx = start_interceptor()
    ctx.host = environ.get('HTTP_HOST', '').split(':')[0]
    ctx.service_name = environ.get('PATH_INFO', '')
    
    query_string = environ.get('QUERY_STRING', '')
    if query_string:
        ctx.service_name += '?{}'.format(query_string)
    
    if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
        1] in conf.web_static_content_extensions:
        ctx.isStaticContents = 'true'
    
    ctx.remoteIp = environ.get('REMOTE_ADDR', '')
    ctx.userAgentString = environ.get('HTTP_USER_AGENT', '')
    ctx.referer = environ.get('HTTP_REFERER''', '')
    
    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = ctx.remoteIp
            pass
        else:
            ctx.userid = ctx.remoteIp  # TODO cookie
    
    datas = [ctx.host,
             ctx.service_name,
             ctx.remoteIp,
             ctx.userAgentString,
             ctx.referer,
             ctx.userid,
             ctx.isStaticContents]
    
    UdpSession.send_packet(PacketTypeEnum.PACKET_REQUEST, ctx, datas)
    
    callback = fn(*args, **kwargs)
    
    if getattr(callback, 'status_code', None):
        status_code = callback.status_code
        errors = [callback.reason_phrase, callback.__class__.__name__]
        interceptor_error(status_code, errors)
    
    end_interceptor()
    return callback


def interceptor_error(status_code, errors):
    # errors: 'error_type', 'error_message'
    ctx = TraceContextManager.getLocalContext()
    ctx.status = int(status_code / 100)
    if ctx.status >= 4 and not ctx.error:
        ctx.error = 1
        try:
            errors.append(traceback.format_exc())
        except:
            errors.append('')
        UdpSession.send_packet(PacketTypeEnum.PACKET_ERROR, ctx, errors)


def interceptor_db_con(fn, db_type, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if ctx.db_opening:
        return fn(*args, **kwargs)
    
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    
    callback = fn(*args, **kwargs)
    
    if not kwargs:
        kwargs = dict(
            x.split('=') for x in re.sub(r'\s*=\s*', '=', args[0]).split())
    
    text = '{}://'.format(db_type)
    text += kwargs.get('user')
    text += "@"
    text += kwargs.get('host')
    text += '/'
    text += kwargs.get('database', kwargs.get('db', kwargs.get('dbname')))
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text
    
    ctx.active_dbc = 0
    
    ctx.db_opening = True
    
    datas = [' ', ' ', 'DB CONNECTION: ' + text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)
    
    return callback


def interceptor_db_execute(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    
    self = args[0]
    try:
        query = args[1].decode()
    except Exception as e:
        query = args[1]
    
    if not query or ctx.active_sqlhash:
        return fn(*args, **kwargs)
    
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    ctx.active_sqlhash = query
    
    errors = []  # 'error_type', 'error_message'
    
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        errors.append(e.__class__.__name__)
        errors.append(e.args[1] if len(e.args) > 1 else \
                          e.args[0])
        try:
            errors.append(traceback.format_exc())
        except:
            errors.append('')
        UdpSession.send_packet(PacketTypeEnum.PACKET_ERROR, ctx, errors)
        
        if not ctx.error:
            ctx.error = 1
    
    finally:
        datas = [ctx.lctx.get('dbc', ''), query]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        UdpSession.send_packet(PacketTypeEnum.PACKET_DB_SQL, ctx,
                               datas)
        
        count = self.rowcount
        if count > -1:
            desc = '{0}: {1}'.format('Fetch count', count)
            datas = [' ', ' ', desc]
            ctx.elapsed = 0
            UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)
        
        ctx.active_sqlhash = 0


def interceptor_db_close(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    ctx.db_opening = False
    
    if not conf.profile_dbc_close:
        return fn(*args, **kwargs)
    
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    
    callback = fn(*args, **kwargs)
    
    text = 'DB: Close Connection.'
    datas = [' ', ' ', text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)
    return callback
