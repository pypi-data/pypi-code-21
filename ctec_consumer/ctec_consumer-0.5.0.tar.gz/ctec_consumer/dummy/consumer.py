# encoding: utf-8
import logging
import os.path
import signal
import sys
from multiprocessing.dummy import Pool as ThreadPool

import pika
from pika import exceptions

import ctec_consumer.consumer_log as log
import ctec_consumer.data_agent as data_agent
from ctec_consumer.data_agent import DataAgent
from models.worker_message import WorkerMessage

reload(sys)
sys.setdefaultencoding('utf-8')

CONSUME_SUCCESS = 0
CONSUME_REDELIVER = 1
CONSUME_REJECT = 2


class Consumer(object):
    def __init__(self, amqp_url, queue, logger=None, prefetch_count=30, thread_num=5, heart_interval=30,
                 consumer_tag=None, is_rpc=False, agent=True, app_name=None, app_desc=None):
        """
        初始化Consumer
        :param amqp_url: 队列amqp地址
        :param queue: 队列名称
        :param logger: logger对象
        :param prefetch_count: 一次拉取消息数量，默认30
        :param thread_num: 线程或进程数量，默认5
        :param heart_interval: 心跳间隔，默认30秒
        :param is_rpc: 是否为RPC服务，默认为False
        :param agent: 是否开启数据代理线程，默认为True
        :param app_name: 应用名称
        :param app_desc: 应用描述
        :return:
        """
        self.logger = logging if logger is None else logger
        self._connection = None
        self._channel = None
        self._closing = False
        self._url = amqp_url + '?heartbeat=' + str(heart_interval)
        self.consumers = []
        self.pool = ThreadPool(thread_num)
        self.queue = queue
        self.handle_message_worker = None
        # 限制单个channel可同时拉取的消息数量
        self.prefetch_count = prefetch_count
        self._consumer_tag = consumer_tag
        self.is_rpc = is_rpc
        self._agent = agent
        if agent:
            if data_agent.ZOOKEEPER_HOSTS is None:
                raise StandardError('未设置zookeeper hosts参数！')
            if app_name is None:
                raise StandardError('未设置应用名称参数！')
            if app_desc is None:
                app_desc = log.APP_NAME

            da = DataAgent(app_name, app_desc, os.path.abspath(os.curdir), queue, amqp_url)
            da.run()

    def connect(self):
        self.logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        self.logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        self.logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                                reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        self.logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.info('Channel opened')
        self._channel = channel
        self._channel.basic_qos(prefetch_count=self.prefetch_count)
        self.add_on_channel_close_callback()
        self.start_consuming()

    def add_on_channel_close_callback(self):
        self.logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        self.logger.warning('Channel %i was closed: (%s) %s',
                            channel, reply_code, reply_text)
        self._connection.close()

    def start_consuming(self):
        self.logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        if self._consumer_tag is None:
            self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                             self.queue)
        else:
            self._channel.basic_consume(self.on_message, self.queue, consumer_tag=self._consumer_tag)

    def add_on_cancel_callback(self):
        self.logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        self.logger.info('Consumer was cancelled remotely, shutting down: %r',
                         method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.logger.info('Received message # %s from %s: %s',
                         basic_deliver.delivery_tag, properties.app_id, body)
        message = WorkerMessage(basic_deliver, properties, body)
        try:
            self.pool.apply_async(self.message_worker, (message,),
                                  callback=self.message_handle_callback)
        except AssertionError:
            self.logger.warning('The thread pool has been shutdown, requeue message tag = %s', message.delivery_tag)
            self._channel.basic_nack(message.delivery_tag)
            # recreate the pool
            self.pool = ThreadPool(getattr(self.pool, '_processes'))

    def message_handle_callback(self, result):
        """
        消息处理回调
        :param result: 消息处理结果，(result_code,result_msg,messages)
        :return:
        """
        result_code, result_msg, message = result
        try:
            if result_code == CONSUME_SUCCESS:
                self._channel.basic_ack(message.delivery_tag)
            elif result_code == CONSUME_REDELIVER:
                self._channel.basic_nack(message.delivery_tag)
            elif result_code == CONSUME_REJECT:
                self.logger.warn('The message will be rejected! delivery_tag = %s', message.delivery_tag)
                self._channel.basic_reject(message.delivery_tag, False)
            else:
                self.logger.warn(
                    'Return code must be CONSUME_SUCCESS/CONSUME_REDELIVER/CONSUME_REJECT. Current code is %s',
                    result_code)
            # 判断是否为rpc服务
            if self.is_rpc:
                self._channel.basic_publish(message.basic_deliver.exchange, message.basic_properties.reply_to,
                                            str(result_msg), message.basic_properties)

            # 消息是否需要转发
            if message.is_publish:
                self._channel.basic_publish(message.exchange, message.routing_key, message.publish_body,
                                            message.publish_properties)

        except exceptions.ChannelClosed:
            self.logger.error('The channel has already been closed!')
        finally:
            # 若开启了代理，则计算消费数量
            if self._agent:
                DataAgent.counter += 1
        self.logger.info('Acknowledging message tag %s, result_code = %s', message.delivery_tag, result_code)

    def stop_consuming(self):
        if self._channel:
            self.logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        self.logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        self.logger.info('Closing the channel')
        self._channel.close()

    def run(self):
        if self.handle_message_worker is None:
            raise Exception('未注册消息处理方法！')
        else:
            # 增加信号
            signal.signal(signal.SIGTERM, self.stop)
            signal.signal(signal.SIGINT, self.stop)
            self._connection = self.connect()
            self._connection.ioloop.start()

    def stop(self):
        self.logger.info('Stopping consumer')
        self._closing = True
        self.stop_consuming()
        # 关闭线程池
        self.pool.close()
        self.pool.join()
        self._connection.ioloop.start()
        self.logger.info('consumer Stopped')

    def close_connection(self):
        self.logger.info('Closing connection')
        self._connection.close()

    def register_worker(self, worker):
        """
        注册实际处理消息的worker
        :param worker: 处理消息方法
        :return:
        """
        self.logger.info("Start register message worker")
        self.handle_message_worker = worker

    def message_worker(self, message):
        """
        处理消息方法
        :param message: 消息对象
        :return:
        """
        self.logger.debug('Start processing message, message tag = %s', message.delivery_tag)
        result = self.handle_message_worker(message)
        if isinstance(result, tuple):
            result_code = result[0]
            result_msg = result[1]
        else:
            result_code = result
            result_msg = None
        self.logger.debug('Messages have been processed. Result code = %s; Result Msg = %s', result_code, result_msg)
        return result_code, result_msg, message
