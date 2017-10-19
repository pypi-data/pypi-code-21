class Sender:
    def __init__(self,rabbit_instance,queue_name):
        self.rabbit = rabbit_instance
        self.exchange_name = '' #direct default
        self.queue_name = queue_name
        self.channel = self.rabbit.channel()
        self.queue = self.rabbit.queue(self.channel,queue_name)

    def bind(self,exchange_name,binding_key):
        self.exchange_name = exchange_name
        self.rabbit.queue_bind(self.channel,exchange_name,self.queue,binding_key)

    def publish(self,routing_key,body,delivery_mode=2):
        self.rabbit.publish(self.channel,self.exchange_name,routing_key,body,delivery_mode=delivery_mode)

