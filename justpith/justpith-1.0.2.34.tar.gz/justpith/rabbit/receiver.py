class Receiver:
    def __init__(self,rabbit_instance,queue_name):
        self.rabbit = rabbit_instance
        self.queue_name = queue_name
        self.channel = self.rabbit.channel()
        self.queue = self.rabbit.queue(self.channel, queue_name)

    def receiver_callback(self,channel, method, properties, body):
        print(" [x] Received %r" % body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def bind(self,exchange_name,binding_key):
        self.exchange_name = exchange_name
        self.rabbit.queue_bind(self.channel,exchange_name,self.queue,binding_key)

    def consume(self,callback,ack=True):
        self.rabbit.consume(channel=self.channel, callback=callback, queue=self.queue_name, ack=ack)

    def num_mess(self):
        return self.rabbit.num_mess(self.channel, self.queue)

    def get(self, num_mess, ack=True):
        return self.rabbit.get(self.channel, self.queue, num_mess, ack)

    def ack(self,delivery_tag, multiple=True):
        # if self.rabbit.connection.is_closed:
        #     self.rabbit.connect()
        #     self.channel = self.rabbit.channel()
        self.rabbit.ack(self.channel,delivery_tag,multiple)

    def nack(self,delivery_tag, multiple=True, requeue=True):
        # if self.rabbit.connection.is_closed:
        #     self.rabbit.connect()
        #     self.channel = self.rabbit.channel()
        self.rabbit.nack(self.channel,delivery_tag,multiple,requeue)
