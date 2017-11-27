# -*- coding: utf-8 -*-
import json
import time
import types
from airbridge.utils.exceptions import ValidationException
from airbridge.utils.tools import get_traceback_str


class QueueWorker():

    def __init__(self, queue_engine, queue_name):
        self.queue_engine = queue_engine
        self.queue_name = queue_name
        self.iter_timespan = 0.5

    def run(self, business_logic):
        if type(business_logic) != types.FunctionType:
            raise Exception("business_logic type should be types.FunctionType")

        self.queue_engine.watch(self.queue_name)

        # 루프를 돌면서 계속해서 가져온다.
        while True:
            try:
                m = self.queue_engine.reserve(timeout=0)
            except Exception as e:
                print('No message to process..')
                self.queue_engine.reconnect()
                self.queue_engine.watch(self.queue_name)
                time.sleep(self.iter_timespan)
                continue

            if m == None:
                time.sleep(self.iter_timespan)
            else:
                try:
                    request = json.loads(m.body)
                    print request
                except:
                    raise ValidationException('Invalid JSON Message in QUEUE.')

                if ('what_to_do' not in request or 'kwargs' not in request):
                    raise ValidationException('Invalid JSON Structure')

                try:
                    business_logic(request['what_to_do'], **request['kwargs'])

                    m.delete()

                except Exception as e:
                    print '** Exception: on {0} :: Message: {1}'.format(request['what_to_do'], str(e))
                    print '** Traceback: {0}'.format(get_traceback_str())
                    traceback_str = get_traceback_str()
                    m.bury()

    def put_message_to_queue(self, what_to_do, delay_seconds=0, **kwargs):
        payloads = {
            'what_to_do': what_to_do,
            'kwargs': kwargs
        }

        self.queue_engine.use(self.queue_name)
        self.queue_engine.put(json.dumps(payloads, ensure_ascii=False).encode('utf-8'))

