# encoding: utf-8
from pika.spec import BasicProperties


class WorkerMessage:
    def __init__(self, basic_deliver, properties, body):
        self.body = body
        self.basic_deliver = basic_deliver
        self.properties = properties.headers
        self.basic_properties = properties
        self.delivery_tag = basic_deliver.delivery_tag
        self.is_publish = False
        self.exchange = None
        self.routing_key = None
        self.publish_properties = None
        self.publish_body = body

    def publish(self, exchange, routing_key, properties=None, expiration=None, body=None):
        """
        设置该消息是否需要转发
        :param exchange: 需要发送的exchange
        :param routing_key: 需要发送的routing key
        :param properties: 需要发送的属性值，字典类型
        :param body: 需要发送的消息体，默认为与原始消息体一致
        :param expiration: 消息的过期时间
        :return:
        """
        self.is_publish = True
        self.exchange = exchange
        self.routing_key = routing_key
        self.publish_properties = BasicProperties(headers=properties, expiration=expiration)
        if body:
            self.publish_body = body
