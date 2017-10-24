# -*- coding: utf-8 -*-

import requests

from ...log import logger


class SendCloudBackend(object):
    """
    sendcloud发送邮件
    """

    SEND_URL = 'http://api.sendcloud.net/apiv2/mail/send'

    def __init__(self, api_user, api_key, sender):
        """
        初始化
        """
        self.api_user = api_user
        self.api_key = api_key
        self.sender = sender

    def emit(self, title, content, receiver_list):
        """
        发送
        """

        params = {
            'apiUser': self.api_user,
            'apiKey': self.api_key,
            'from': self.sender,
            'to': ';'.join(receiver_list),
            'subject': title,
            'plain': content,
        }

        try:
            rsp = requests.post(self.SEND_URL, params, verify=False)

            if not rsp.json()['result']:
                logger.error('send fail. status: %s, text: %s, params: %s', rsp.status_code, rsp.text, params)
                return False
            else:
                return True

        except:
            logger.error('exc occur. params: %s', params, exc_info=True)
            return False
