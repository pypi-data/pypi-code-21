# -*- coding: utf-8 -*-
# Created by lijian on 2017/6/30.
import smtplib
from email.header import Header
from email.utils import parseaddr, formataddr


class Email(object):
    def __init__(self, smtp_server, smtp_port, smtp_server_username, smtp_server_password):
        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port
        self.__smtp_server_username = smtp_server_username
        self.__smtp_server_password = smtp_server_password
        self.__server = self.set_up()

    def set_up(self):
        if not hasattr(self, "__server"):
            server = smtplib.SMTP(self.__smtp_server, self.__smtp_port)
            server.set_debuglevel(1)
            server.login(self.__smtp_server_username, self.__smtp_server_password)
            return server
        else:
            return self.__server

    @classmethod
    def format_address(cls, address):
        name, addr = parseaddr(address)
        return formataddr((Header(name, 'utf-8').encode(),
                           addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def send(self, to_address, msg):
        """
        发送邮件
        :param to_address: (list)
        :param msg: (str)
        :return:
        """
        msg['From'] = self.format_address(u'<%s>' % self.__smtp_server_username)
        msg['To'] = ",".join([self.format_address(u'<%s>' % address) for address in to_address])
        self.__server.sendmail(self.__smtp_server_username, to_address, msg.as_string())

    def get_smtp_server(self):
        return self.get_smtp_server()

    def set_smtp_server(self, smtp_server):
        self.__smtp_server = smtp_server

    def get_smtp_port(self):
        return self.__smtp_port

    def set_smtp_port(self, smtp_port):
        self.__smtp_port = smtp_port

    def get_smtp_server_username(self):
        return self.__smtp_server_username

    def set_smtp_server_username(self, smtp_server_username):
        self.__smtp_server_username = smtp_server_username

    def get_smtp_password(self):
        return self.__smtp_server_password

    def set_smtp_password(self, smtp_server_password):
        self.__smtp_server_password = smtp_server_password

    def __del__(self):
        self.__server.quit()
