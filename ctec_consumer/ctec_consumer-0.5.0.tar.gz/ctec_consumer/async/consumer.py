# encoding: utf-8
import logging
import os.path
import signal
import sys
import threading
import time
from Queue import Queue, Empty
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
                 consumer_tag=None, is_rpc=False, batch_num=1, agent=True, app_name=None, app_desc=None):
        """
        初始化Consumer
        :param amqp_url: 队列amqp地址
        :param queue: 队列名称
        :param logger: logger对象
        :param prefetch_count: 一次拉取消息数量，默认30
        :param thread_num: 线程或进程数量，默认5
        :param heart_interval: 心跳间隔，默认30秒
        :param is_rpc: 是否为RPC服务，默认为False
        :param batch_num: 批量消费消息数量，默认为1
        :param agent: 是否开启数据代理线程，默认为True
        :param app_name: 应用名称
        :param app_desc: 应用描述
        :return:
        """
        self.logger = logging if logger is None else logger
        self._connection = None
        self._old_connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = consumer_tag
        self._url = amqp_url + '?heartbeat=' + str(heart_interval)
        self.pool = ThreadPool(thread_num)
        self.queue = queue
        self.handle_message_worker = None
        # 限制单个channel可同时拉取的消息数量
        self.prefetch_count = prefetch_count
        self.is_rpc = is_rpc
        self.batch_q = Queue(batch_num)

        wt = threading.Thread(target=self.worker_thread)
        wt.setDaemon(True)
        wt.start()

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
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        self.logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def worker_thread(self):
        while 1:
            if self.batch_q.empty():
                time.sleep(0.5)
                continue
            messages = list()
            for _ in xrange(self.batch_q.maxsize):
                try:
                    messages.append(self.batch_q.get_nowait())
                except Empty:
                    break

            try:
                self.pool.apply_async(self.message_worker, (messages,),
                                      callback=self.message_handle_callback)
            except AssertionError:
                self.logger.warning('The thread pool has been shutdown, requeue messages count = %s', len(messages))
                for message in messages:
                    if message is not None:
                        self._channel.basic_nack(message.delivery_tag)
                # recreate the pool
                self.pool = ThreadPool(getattr(self.pool, '_processes'))

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        self.logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        self.logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                                reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        self.logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        self.logger.info('Channel opened')
        self._channel = channel
        self._channel.basic_qos(prefetch_count=self.prefetch_count)
        self.add_on_channel_close_callback()
        self.start_consuming()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        self.logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        self.logger.warning('Channel %i was closed: (%s) %s',
                            channel, reply_code, reply_text)
        self._connection.close()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        self.logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        if self._consumer_tag is None:
            self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                             self.queue)
        else:
            self._channel.basic_consume(self.on_message, self.queue, consumer_tag=self._consumer_tag)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        self.logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        self.logger.info('Consumer was cancelled remotely, shutting down: %r',
                         method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        self.logger.info('Received message # %s from %s: %s',
                         basic_deliver.delivery_tag, properties.app_id, body)
        message = WorkerMessage(basic_deliver, properties, body)
        self.batch_q.put(message)

    def message_handle_callback(self, result):
        """
        消息处理回调
        :param result: 消息处理结果，(result_code,result_msg,messages)
        :return: 
        """
        result_code, result_msg, messages = result
        try:
            for message in messages:
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

                self.batch_q.task_done()
        except exceptions.ChannelClosed:
            self.logger.error('The channel has already been closed!')
        finally:
            # 若开启了代理，则计算消费数量
            if self._agent:
                DataAgent.counter += 1
        self.logger.info('Acknowledging message count %s, result_code = %s', len(messages), result_code)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            self.logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        self.logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        self.logger.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        if self.handle_message_worker is None:
            raise Exception('未注册消息处理方法！')
        else:
            # 增加信号
            signal.signal(signal.SIGTERM, self.stop)
            signal.signal(signal.SIGINT, self.stop)
            self._connection = self.connect()
            self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        self.logger.info('Stopping consumer')
        self._closing = True
        self.stop_consuming()
        # 关闭线程池
        self.pool.close()
        self.pool.join()
        self._connection.ioloop.start()
        self.logger.info('consumer Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
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

    def message_worker(self, messages):
        """
        处理消息方法
        :param messages: 消息对象数组
        :return:
        """
        self.logger.debug('Start processing message, message count = %s', len(messages))
        result = self.handle_message_worker(messages)
        if isinstance(result, tuple):
            result_code = result[0]
            result_msg = result[1]
        else:
            result_code = result
            result_msg = None
        self.logger.debug('Messages have been processed. Result code = %s; Result Msg = %s', result_code, result_msg)
        return result_code, result_msg, messages
