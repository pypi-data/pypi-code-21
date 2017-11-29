
import pika

class Producer(object):

    def __init__(self,connection_str,username,passwd,queue_tunnel):
        if connection_str.find(':') == -1:
            raise Exception('connection str wrong')
        _ip = connection_str[:connection_str.find(':')]
        _port = connection_str[connection_str.find(':') + 1:]
        credentials = pika.PlainCredentials(username, passwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(_ip, _port, '/', credentials))#5672
        channel = connection.channel()
        channel.queue_declare(queue=queue_tunnel)#'request.trace.log'
        self.channel = channel

    def send(self,message):
        return self.channel.basic_publish(exchange='',
                              routing_key='request.trace.log',
                              body=message)


class Consumer(object):
    def __init__(self, connection_str, username, passwd, queue_tunnel):
        if connection_str.find(':') == -1:
            raise Exception('connection str wrong')
        _ip = connection_str[:connection_str.find(':')]
        _port = connection_str[connection_str.find(':') + 1:]
        credentials = pika.PlainCredentials(username, passwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(_ip, _port, '/', credentials))  # 5672
        channel = connection.channel()
        channel.queue_declare(queue=queue_tunnel)  # 'request.trace.log'
        channel.basic_consume(self.callback,
                              queue=queue_tunnel,
                              no_ack=True)
        self.channel = channel
        # channel.start_consuming()

    def callback(self,ch, method, properties, body):
        print('get mq data success')
        from ..func_plus import FuncHelper
        print(" [x] mq Received %r" % FuncHelper.bytes_str_decode_str(body))

    def start(self):
        self.channel.start_consuming()

from ..setting import sweet_settings

if sweet_settings.get('mqLogEnabled',False):
    connectionString = sweet_settings['mq']['connectionString']
    user = sweet_settings['mq']['user']
    password = sweet_settings['mq']['password']
    traceLogQueueName = sweet_settings['mq']['traceLogQueueName']
    if not hasattr(Consumer,'consumer'):
        Consumer.consumer = Consumer(connectionString, user, password, traceLogQueueName)
        import threading
        thread_rabbitmq_consumer = threading.Thread(target=Consumer.consumer.start, args=())
        thread_rabbitmq_consumer.daemon = True
        thread_rabbitmq_consumer.start()