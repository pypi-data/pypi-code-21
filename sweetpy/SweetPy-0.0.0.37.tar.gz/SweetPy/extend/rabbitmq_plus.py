
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
        channel.start_consuming()

    def callback(ch, method, properties, body):
        print(" [x] mq Received %r" % body)

