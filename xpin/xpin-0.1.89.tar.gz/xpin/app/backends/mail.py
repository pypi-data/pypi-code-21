# -*- coding: utf-8 -*-

import copy
import random

from ...log import logger


class MailBackend(object):
    """
    发送邮件
    """

    def __init__(self, sender_list):
        """
        初始化
        sender_list可以保证只要发送失败就尝试下一个
        """
        self.sender_list = sender_list

    def emit(self, title, content, receiver_list):
        """
        发送
        """

        sender_list = copy.deepcopy(self.sender_list)

        while sender_list:
            random.shuffle(sender_list)

            # 取出最后一个
            params = sender_list.pop()

            try:
                self._sendmail(params['host'], params['port'], params['sender'],
                               receiver_list, title, content,
                               username=params['username'], password=params['password'],
                               use_ssl=params['use_ssl'], use_tls=params['use_tls'],
                               )
                return True
            except:
                logger.error('exc occur. params: %s', params, exc_info=True)
        else:
            # 就是循环完了，也没发送成功
            return False

    def _sendmail(self, host, port, sender, receiver_list, subject, content,
                  content_type='plain', encoding='utf-8',
                  username=None, password=None, use_ssl=False, use_tls=False, debuglevel=0
                  ):
        """
        发送邮件
        content_type: plain / html
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formatdate

        mail_msg = MIMEText(content, content_type, encoding)
        mail_msg['Subject'] = Header(subject, encoding)
        mail_msg['From'] = sender
        mail_msg['To'] = ', '.join(receiver_list)
        mail_msg['Date'] = formatdate()

        if use_ssl:
            mail_client = smtplib.SMTP_SSL(host, port)
        else:
            mail_client = smtplib.SMTP(host, port)

        mail_client.set_debuglevel(debuglevel)

        if use_tls:
            mail_client.starttls()

        if username and password:
            mail_client.login(username, password)

        # 发邮件
        mail_client.sendmail(sender, receiver_list, mail_msg.as_string())
        mail_client.quit()
