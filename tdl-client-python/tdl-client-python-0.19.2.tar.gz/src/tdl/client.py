import datetime

__author__ = 'tdpreece'
import logging
import time
import json
from collections import OrderedDict
from threading import Timer

import stomp

logger = logging.getLogger('tdl.client')
logger.addHandler(logging.NullHandler())


class Client(object):
    def __init__(self, hostname, unique_id, port=61613, request_timeout_millis=500):
        self.hostname = hostname
        self.port = port
        self.unique_id = unique_id
        self.request_timeout_millis = request_timeout_millis
        self.total_processing_time_millis = 0
        self.__start_time = None
        self.__end_time = None
        self.__timer = None

    def get_request_timeout_millis(self):
        return self.request_timeout_millis

    def go_live_with(self, processing_rules):
        self.__start_time = datetime.datetime.now()
        self.run(ApplyProcessingRules(processing_rules))

    def run(self, handling_strategy):
        try:
            print('Starting client')

            remote_broker = RemoteBroker(self.hostname, self.port, self.unique_id, self.request_timeout_millis)
            remote_broker.subscribe(handling_strategy)

            print('Waiting for requests')
            # DEBT - this is just to block.
            while remote_broker.is_connected():
                time.sleep(0.1)

            self.__end_time = datetime.datetime.now()
            difference = self.__end_time - self.__start_time
            self.total_processing_time_millis = difference.total_seconds() * 1000.00

        except Exception as e:
            print('There was a problem processing messages')
            logger.exception('Problem communicating with the broker.')


class ApplyProcessingRules(object):
    def __init__(self, processing_rules):
        self.processing_rules = processing_rules

    def process_next_message_from(self, remote_broker, headers, message):
        # Decode request
        try:
            decoded_message = json.loads(message)
            method = decoded_message['method']
            params = decoded_message['params']
            id = decoded_message['id']
        except:
            decoded_message = ''
            method = ''
            params = ''
            id = ''
            print('Invalid message format')
            action = 'stop'

        # Match implementation
        if method not in self.processing_rules.rules:
            user_result_message = 'error = "method \'{}\' did not match any processing rule", (NOT PUBLISHED)'.format(method)
            action = 'stop'
        else:
            implementation = self.processing_rules.rules[method].user_implementation
            try:
                result = implementation(*params)
                action = self.processing_rules.rules[method].client_action

                if 'publish' in action:
                    user_result_message = 'resp = {}'.format(self.get_parameter_msg(result))
                else:
                    user_result_message = 'resp = {}, (NOT PUBLISHED)'.format(self.get_parameter_msg(result))

            except Exception as e:
                result = ''
                logger.exception('The user implementation has thrown an exception: {}'.format(e.message))
                user_result_message = 'error = "user implementation raised exception", (NOT PUBLISHED)'
                action = 'stop'

            if 'publish' in action:
                response = OrderedDict([
                    ('result', result),
                    ('error', None),
                    ('id', id),
                ])

                remote_broker.acknowledge(headers)
                remote_broker.publish(response)

        self.print_user_message(params, user_result_message, id, method)
        if 'stop' in action:
            remote_broker.conn.unsubscribe(1)
            remote_broker.conn.remove_listener('listener')

    def print_user_message(self, params, user_result_message, id, method):
        params_str = ", ".join([self.get_parameter_msg(p) for p in params])
        print('id = {id}, req = {method}({params}), {user_result_message}'.format(id=id, method=method, params=params_str,
                                                                                  user_result_message=user_result_message))

    @staticmethod
    def get_parameter_msg(parameter):
        if not isinstance(parameter, basestring):
            return str(parameter)
        lines = str(parameter).split('\n')
        if len(lines) == 1:
            return '"{}"'.format(lines[0])
        if len(lines) == 2:
            return '"{} .. ( 1 more line )"'.format(lines[0])
        return '"{} .. ( {} more lines )"'.format(lines[0], len(lines) - 1)


class Listener(stomp.ConnectionListener):
    def __init__(self, remote_broker, handling_strategy, start_timer, stop_timer):
        self.remote_broker = remote_broker
        self.handling_strategy = handling_strategy
        self.start_timer = start_timer
        self.stop_timer = stop_timer

    def on_message(self, headers, message):
        self.stop_timer()
        self.handling_strategy.process_next_message_from(self.remote_broker, headers, message)
        self.start_timer()


class RemoteBroker(object):
    def __init__(self, hostname, port, unique_id, request_timeout_millis):
        hosts = [(hostname, port)]
        connect_timeout = 10
        self.conn = stomp.Connection(host_and_ports=hosts, timeout=connect_timeout)
        self.conn.start()
        self.conn.connect(wait=True)
        self.unique_id = unique_id
        self.request_timeout_millis = request_timeout_millis

    def acknowledge(self, headers):
        self.conn.ack(headers['message-id'], headers['subscription'])

    def publish(self, response):
        self.conn.send(
                body=json.dumps(response, separators=(',', ':')),
                destination='{}.resp'.format(self.unique_id)
        )

    def subscribe(self, handling_strategy):
        listener = Listener(self, handling_strategy, self.start_timer, self.stop_timer)
        self.conn.set_listener('listener', listener)
        self.conn.subscribe(
                destination='{}.req'.format(self.unique_id),
                id=1,
                ack='client-individual'
        )
        self.start_timer()

    def close(self):
        print('Stopping client')
        self.conn.disconnect()

    def is_connected(self):
        return self.conn.is_connected()

    def stop_timer(self):
        if self.__timer is not None:
            self.__timer.cancel()

    def start_timer(self):
        self.__timer = Timer(self.request_timeout_millis / 1000.00, self.close)
        self.__timer.start()
