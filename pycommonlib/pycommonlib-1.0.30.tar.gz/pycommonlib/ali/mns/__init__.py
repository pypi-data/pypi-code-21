import base64, json
from . import xml_helper

class Message(object):
    def __init__(self, data, delaySeconds=0, priority=10):
        assert isinstance(data, dict) or isinstance(data, str)
        if isinstance(data, dict):
            self.body = json.dumps(data)
        elif isinstance(data, str):
            self.body = data
        self.body = str(base64.b64encode(self.body.encode()), 'utf-8')
        self.delaySeconds = delaySeconds
        self.priority = priority
        
        
    def to_xml(self):
        message = {'MessageBody':self.body, 'DelaySeconds':self.delaySeconds, 'Priority':self.priority}
        xml = xml_helper.dict_to_xml(message, 'http://mns.aliyuncs.com/doc/v1/', 'Message')
        return xml
    
    
class ReceivedMessage(object):
    
    def __init__(self, messageId, receiptHandler, data, priority):
        self.messageId = messageId
        self.receiptHandler = receiptHandler
        self.data = data
        self.priority = priority
        
    @property
    def MessageId(self):
        return self.messageId
    
    @property
    def ReceiptHandler(self):
        return self.receiptHandler
    
    @property
    def Data(self):
        return self.data
    
    @property
    def Priority(self):
        return self.priority
    
    
    @staticmethod
    def parse(recv_msg):
        data = json.loads(str(base64.b64decode(recv_msg['MessageBody'].encode()), 'utf-8'))
        return ReceivedMessage(recv_msg['MessageId'], recv_msg['ReceiptHandle'], data, recv_msg['Priority'])
    
