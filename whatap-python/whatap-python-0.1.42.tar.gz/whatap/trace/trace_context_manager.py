import os
import random
import threading

from whatap import logging
from whatap.conf.configure import Configure as conf
from whatap.io.data_inputx import DataInputX
from whatap.io.data_outputx import DataOutputX
from whatap.util.linked_map import LinkedMap


class TraceContextManager(object):
    entry = LinkedMap()
    local = threading.local()
    
    @classmethod
    def keys(cls):
        return cls.entry.keys()
    
    @classmethod
    def getActiveCount(cls):
        act = [0 for _ in range(3)]
        try:
            en = cls.entry.values()
            while en.hasMoreElements():
                ctx = en.nextElement()
                elapsed = ctx.getElapsedTime()
                if elapsed < conf.trace_active_transaction_yellow_time:
                    act[0] += 1
                elif elapsed < conf.trace_active_transaction_red_time:
                    act[1] += 1
                else:
                    act[2] += 1
        
        except Exception as e:
            logging.debug(e, extra={'id': 'WA310'}, exc_info=True)
        
        return act
    
    @classmethod
    def getContextEnumeration(cls):
        return cls.entry.values()
    
    @classmethod
    def getContext(cls, key):
        return cls.entry.get(key)
    
    @classmethod
    def getLocalContext(cls):
        if not bool(cls.local.__dict__):
            cls.local.context = None
        
        return cls.local.context
    
    @classmethod
    def getId(cls):
        dout = DataOutputX()
        dout.writeFloat(random.random() * random.choice([-1, 1]))
        dout.writeFloat(random.random())
        din = DataInputX(dout.buffer.getvalue())
        key = din.readLong()
        return key
    
    @classmethod
    def start(cls, o, thread_id):
        dout = DataOutputX()
        dout.writeInt(os.getpid())
        dout.writeInt(0)
        din = DataInputX(dout.buffer.getvalue())
        key = din.readLong() + thread_id
        cls.local.context = o
        cls.entry.put(key, o)
        return key
    
    @classmethod
    def parseThreadId(cls, key):
        pid = os.getpid()
        dout = DataOutputX()
        dout.writeInt(pid)
        dout.writeInt(0)
        din = DataInputX(dout.buffer.getvalue())
        thread_id = key - din.readLong()
        return thread_id, pid
    
    @classmethod
    def end(cls, key):
        cls.local.context = None
        cls.entry.remove(key)
    
    @classmethod
    def getTxProfile(cls, n):
        ctx = cls.getLocalContext()
        if not ctx:
            return None
        return ctx.profile.getLastSteps(n)
