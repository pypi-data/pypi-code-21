from collections import defaultdict
from whatap.trace import UdpSession, PacketTypeEnum, get_dict
from whatap.trace.mod.application_wsgi import trace_handler
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context_manager import TraceContextManager

from whatap import logging


def instrument_plugin(module_dict):
    module = module_dict['module_name']
    class_name = module_dict.get('class_name')
    if class_name:
        module = getattr(module, module_dict['class_name'])
    else:
        class_name = 'class_name'
    target = module_dict['def_name']
    
    key = module.__module__ if isinstance(module, type) else module.__name__
    setattr(instrument_plugin, key, defaultdict(dict))
    getattr(instrument_plugin, key)[class_name][target] = {}
    getattr(instrument_plugin, key)[class_name][target][
        'name'] = '{}.{}.{}'.format(key, class_name, target)
    getattr(instrument_plugin, key)[class_name][target]['args_indexes'] = \
        module_dict['args_indexes'].split(',')
    getattr(instrument_plugin, key)[class_name][target]['kwargs'] = \
        module_dict[
            'kwargs'].split(',')
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            data_dict = {}
            args_dict = {}
            kwargs_dict = {}
            
            try:
                if repr(fn).replace('\'', '').find(' of ') > -1:
                    ins = repr(fn).replace('\'', '').split()[-2].split('.')
                    data_dict = getattr(instrument_plugin, ins[0])[ins[1]][
                        fn.__name__]
                else:
                    ins = repr(fn).replace('\'', '').split()[1].split('.')
                    if len(ins) == 1:
                        ins.insert(0, 'class_name')
                        
                    data_dict = getattr(instrument_plugin, fn.__module__)
                    for i, v in enumerate(ins):
                        data_dict = data_dict[v]
                
                if data_dict['args_indexes'][0] or data_dict['kwargs'][0]:
                    for i in data_dict['args_indexes']:
                        args_dict['args{}'.format(i)] = args[int(i) - 1]
                    for key in data_dict['kwargs']:
                        if not key:
                            key = 'kwargs'
                        kwargs_dict['{}'.format(key)] = kwargs.get(key, '')
            except Exception as e:
                logging.debug(format(repr(fn).replace('\'', '')), extra={'id': 'PLUGIN PARSING ERROR'})
            finally:
                ctx = TraceContextManager.getLocalContext()
                start_time = DateUtil.nowSystem()
                ctx.start_time = start_time
                callback = fn(*args, **kwargs)
                ctx.elapsed = DateUtil.nowSystem() - start_time
                
                desc = 'Plugin: {}\n'.format(data_dict.get('name'))
                if args_dict:
                    desc += '{}\n'.format(args_dict)
                if kwargs_dict:
                    desc += '{}'.format(kwargs_dict)
                datas = [' ', ' ', desc]
                
                UdpSession.send_packet(PacketTypeEnum.PACKET_MSG, ctx, datas)

                return callback
        
        return trace
    
    try:
        setattr(module, target, wrapper(getattr(module, target)))
    except Exception as e:
        get_dict(module)[target] = wrapper(getattr(module, target))
