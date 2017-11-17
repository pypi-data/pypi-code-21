import pika

from .rabbit_setting import no_ack
from .rabbit_setting import delivery_mode


class Rabbit:
    def __init__(self,host="localhost"):
        self.connection = None
        self.no_ack = no_ack
        self.delivery_mode = delivery_mode
        self.host = host
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))

    def disconnect(self):
        self.connection.close()

    def channel(self):
        return self.connection.channel()

    def queue(self,channel,queue_name,durable=True):
        return channel.queue_declare(queue=queue_name,durable=durable)

    def queue_bind(self,channel,exchange,queue,binding_key=''):
        channel.queue_bind(exchange=exchange,
                           queue=queue.method.queue,
                           routing_key=binding_key)


    def publish(self,channel,exchange,routing_key,body, delivery_mode=2):
        channel.basic_publish(exchange=exchange,
                              routing_key=routing_key,
                              body=body,
                              properties=pika.BasicProperties(
                                  delivery_mode=delivery_mode,  # make message persistent
                              ))

    def consume(self,channel,callback,queue,ack=True):
        """
        :param channel: il canale verso il server 
        :param callback: la funzione che gestisce il messaggio in input
        :param queue: il nome della coda da cui leggere
        :param ack: se il server si aspetta un ack prima di scartare il messaggio
        :return: 
        """
        channel.basic_consume(callback,
                              queue=queue,
                              no_ack=not ack)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def num_mess(self,channel,queue):
        return queue.method.message_count

    def get(self,channel,queue,num_mess,ack=True):
        messages = []
        method_frame = None
        queue_name = queue.method.queue
        for x in range(num_mess):
            method_frame, header_frame, body = channel.basic_get(queue_name)
            messages.append(body.decode("utf8"))
            if ack == True:
                channel.basic_ack(method_frame.delivery_tag)

        if    method_frame is None: return messages,None
        return messages, method_frame.delivery_tag

    def ack(self,channel, delivery_tag, multiple=True):
        channel.basic_ack(delivery_tag, multiple=multiple)

    def nack(self,channel, delivery_tag, multiple=True, requeue=True):
        channel.basic_nack(delivery_tag, multiple=multiple, requeue=requeue)