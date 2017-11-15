# -*- coding: utf-8 -*-
import sys
import logging
import pika
from pymqo.base import Base
from urllib.parse import urlparse, ParseResult, parse_qsl, unquote, urlunparse, urlencode

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
logger = logging.getLogger(__name__)


# TODO: support python 2
# if sys.version_info >= (3,):
#     from urllib.parse import urlparse, urlencode, parse_qsl, unquote
# else:
#     from urlparse import urlparse



class RabbitMQObject(Base):
    __connection = None
    __channel = None

    __url = None
    __exchange = None
    __exchange_type = None
    __queue_name = None
    __routing_key = None

    __username = ''
    __password = ''
    __host = ''
    __port = 5672
    __vhost = ''
    __query = ''

    __is_connecting = False
    __is_closing = False
    _message = False

    def __init__(self, ampq_url=None, scheme=None, username=None, password=None, host=None, port=None, vhost=None,
                 query=None, exchange=None, exchange_type=None, routing_key=None, consume_callback=None):
        if ampq_url is not None:
            self.url = ampq_url
            parse_result = urlparse(ampq_url)
            self.username = parse_result.username
            self.password = parse_result.password
            self.scheme = parse_result.scheme
            self.host = parse_result.hostname
            self.port = parse_result.port
            self.vhost = unquote(parse_result.path[1:]) if parse_result.path[0] == '/' else unquote(
                parse_result.path)
            self.query = dict(parse_qsl(parse_result.query))
        else:
            self.username = username
            self.password = password
            self.scheme = scheme
            self.host = host
            self.port = port
            self.vhost = vhost
            self.query = query

        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.consume_callback = consume_callback

    def build_amqp_url(self):
        netloc = ''
        if self.host != '' and self.host is not None:
            netloc = self.host
            if self.port is not None:
                netloc += (':' + str(self.port))
            authority = ''
            if self.username != '' and self.username is not None:
                authority += self.username
                if self.password != '' and self.password is not None:
                    authority += (':' + self.password)
                netloc = (authority + '@' + netloc)
        if self.query is not None and any(self.query):
            query_string = '?' + urlencode(self.query)
        else:
            query_string = ''
        url = '{}://{}/{}{}'.format(self.scheme, netloc, self.vhost, query_string)
        return url

    def connect(self):
        if self.is_connected():
            return self.connection
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=pika.PlainCredentials(
                    username=self.username,
                    password=self.password
                )
            ))
            self.__channel = self.connection.channel()
            self.__channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
            self.__is_closing = False
        except:
            exc_info = sys.exc_info()
            logger.info(exc_info)
            self.connection = None
        return self.connection

    def close(self):
        try:
            self.__is_closing = True
            self.connection.close()
        except:
            exc_info = sys.exc_info()
            logger.info(exc_info)
            return False
        return True

    def basic_publish(self, message, exchange=None, routing_key=None):
        if not self.is_connected():
            self.connect()
        if not self.is_connected():
            return False
        try:
            if exchange is None:
                exchange = self.exchange
            if routing_key is None:
                routing_key = self.routing_key
            self.__channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        except:
            exc_info = sys.exc_info()
            logger.info(exc_info)
            return False
        return True

    def basic_consume(self, exchange=None, no_ack=True):
        if not self.is_connected():
            self.connect()
        try:
            if exchange is None:
                exchange = self.exchange
            result = self.__channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            self.__channel.queue_bind(exchange=exchange, queue=queue_name)
            self.__channel.basic_consume(self.on_comsume, queue=queue_name, no_ack=no_ack)
            self.__channel.start_consuming()
        except:
            exc_info = sys.exc_info()
            logger.info(exc_info)

    def on_comsume(self, ch, method, properties, body):
        self.consume_callback(body)

    def get_message(self):
        return self._message

    def get_connection(self):
        return self.__connection

    def set_connection(self, cnt=None):
        if cnt is not None:
            self.__connection = cnt

    def get_url(self):
        return self.__url

    def set_url(self, url=None):
        if url is not None:
            self.__url = url

    def get_exchange(self):
        return self.__exchange

    def set_exchange(self, exchange=None):
        if exchange is not None:
            self.__exchange = exchange

    def get_exchange_type(self):
        return self.__exchange_type

    def set_exchange_type(self, exchange_type=None):
        if exchange_type is not None:
            self.__exchange_type = exchange_type

    def get_queue_name(self):
        return self.__queue_name

    def set_queue_name(self, queue_name=None):
        if queue_name is not None:
            self.__queue_name = queue_name

    def get_routing_key(self):
        return self.__routing_key

    def set_routing_key(self, routing_key=None):
        if routing_key is not None:
            self.__routing_key = routing_key

    def get_username(self):
        return self.__username

    def set_username(self, username=None):
        if username is not None:
            self.__username = username

    def get_password(self):
        return self.__password

    def set_password(self, password=None):
        if password is not None:
            self.__password = password

    def get_scheme(self):
        return self.__scheme

    def set_scheme(self, scheme=None):
        if scheme is None:
            scheme = 'amqp'
        self.__scheme = scheme

    def get_host(self):
        return self.__host

    def set_host(self, host=None):
        if host is not None:
            self.__host = host

    def get_port(self):
        if self.__port is not None and self.__port in range(1, 65536):
            return self.__port
        return None

    def set_port(self, port=None):
        if port is None and port not in range(1, 65536):
            port = 5672
        self.__port = int(port)

    def get_vhost(self):
        return self.__vhost

    def set_vhost(self, vhost=None):
        if vhost is None:
            vhost = '/'
        self.__vhost = vhost

    def get_query(self):
        return self.__query

    def set_query(self, query=None):
        if query is not None:
            self.__query = query

    def is_connected(self):
        return self.connection is not None

    connection = property(fset=set_connection, fget=get_connection)
    url = property(fset=set_url, fget=get_url)
    exchange = property(fset=set_exchange, fget=get_exchange)
    exchange_type = property(fset=set_exchange_type, fget=get_exchange_type)
    queue_name = property(fset=set_queue_name, fget=get_queue_name)
    routing_key = property(fset=set_routing_key, fget=get_routing_key)
    username = property(fset=set_username, fget=get_username)
    password = property(fset=set_password, fget=get_password)
    scheme = property(fset=set_scheme, fget=get_scheme)
    host = property(fset=set_host, fget=get_host)
    port = property(fset=set_port, fget=get_port)
    vhost = property(fset=set_vhost, fget=get_vhost)
    query = property(fset=set_query, fget=get_query)
