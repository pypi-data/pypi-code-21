#! /usr/bin/env python
# coding: utf-8

import base64
import threading
from JYAliYun import XML_CONTENT
from JYAliYun.Tools import jy_requests
from JYAliYun.Tools import ConvertObject
from JYAliYun.AliYunObject import ObjectManager

__author__ = 'ZhouHeng'


class MNSTopicsManager(ObjectManager):
    PRODUCT = "MNS"
    version = "2015-06-06"

    def __init__(self, topic_name, *args, **kwargs):
        kwargs["logger_name"] = "MNS_TOPICS_MESSAGE"
        super(MNSTopicsManager, self).__init__(*args, **kwargs)
        self.topic_name = topic_name
        self.message_tag = None
        self.message_attributes = None

    def publish_message(self, message_body, message_tag=None, message_attributes=None, is_thread=True):
        if is_thread is True:
            t = threading.Thread(target=self.publish_message, args=[message_body, message_tag, message_attributes,
                                                                    False])
            t.daemon = True
            t.start()
            return None
        self.info_log(["PUBLISH MESSAGE [", message_tag, "]", message_body])
        message_body += "\n[%s]" % self.env
        base64_message_body = base64.b64encode(ConvertObject.encode(message_body))
        data = {"MessageBody": base64_message_body}
        if message_tag is not None:
            data["MessageTag"] = message_tag
        if message_attributes is not None:
            data["MessageAttributes"] = message_attributes
        resource = "/topics/%s/messages" % self.topic_name
        headers = self.ali_headers("POST", resource, headers={"x-mns-version": self.version}, content_type=XML_CONTENT)

        xml_data = ConvertObject.dict_to_xml("Message", data)
        url = self.server_url + resource
        r_d = jy_requests.post(url, data=xml_data, headers=headers, no_exception=True)
        if r_d.status_code / 100 != 2:
            self.waring_log(["PUBLISH MESSAGE [", message_tag, "]", message_body],
                            "RETURN %s %s" % (r_d.status_code, r_d.text), "ERROR", r_d.error)
        return r_d
