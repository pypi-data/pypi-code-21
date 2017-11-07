from urllib import parse
from . import http_client, Message, ReceivedMessage, xml_helper

class Queue(object):
    def __init__(self, name, endpoint):
        self.name = name
        self.endpoint = endpoint

    def __str__(self, *args, **kwargs):
        return 'queue {}'.format(self.name)

    def _composeUrl(self, path):
        return parse.urljoin(self.endpoint, path)

    def send_message(self, message):
        assert isinstance(message, Message)
        resp = http_client.post(self._composeUrl('messages'), message.to_xml(), valid_codes=(201, ))
        return xml_helper.xml_to_dic('Message', resp[1])

    def receive_message(self, waitseconds):
        resp = http_client.get(
            self._composeUrl('messages'), params={'waitseconds': waitseconds}, valid_codes=(200, 404))
        if resp[0] == 404:
            return None
        else:
            return ReceivedMessage.parse(xml_helper.xml_to_dic('Message', resp[1]))

    def delete_message(self, receiptHandle):
        http_client.delete(
            self._composeUrl('messages'), '', params={'ReceiptHandle': receiptHandle}, valid_codes=(204, 404))
