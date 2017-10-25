# encoding: utf-8

from modislock_monitor.config import load_config
from modislock_monitor.database import Database, Settings, SettingsValues
from sqlalchemy import and_

config = load_config()


class Message:
    """Message to send in notifications

    """

    def __init__(self):
        self.__subject = config.MAIL_SUBJECT_PREFIX
        self.__sender = config.MAIL_DEFAULT_SENDER
        self.__destination = list()
        self.__header = ''
        self.__body = ''
        self.__text = ''

    @property
    def subject(self):
        """Subject of email

        :returns: Subject string

        """
        return self.__subject

    @subject.setter
    def subject(self, subj):
        """Set subject of email

        :param str subj:

        """
        self.__subject = subj

    @property
    def sender(self):
        """Sender of email

        :returns: Email sender

        """
        return self.__sender

    @sender.setter
    def sender(self, send_user):
        """Set sender

        :param str send_user:

        """
        self.__sender = send_user

    @property
    def destination(self):
        """Destination email of message

        :returns: destination string

        """
        return self.__destination

    @destination.setter
    def destination(self, dest):
        """Sets destination of message

        :param str dest: email of destination

        """
        for d in dest:
            self.__destination.append(d)

    @property
    def header(self):
        """Header of message

        :returns: header of email

        """
        return self.__header

    @header.setter
    def header(self, head):
        """Sets the header of the email

        :param str head:

        """
        self.__header = head

    @property
    def body(self):
        """Body of email

        :returns: body of email

        """
        return self.__body

    @body.setter
    def body(self, bdy):
        """Set body of email

        :param str bdy:

        """
        self.__body = bdy

    @property
    def text(self):
        """Text of email

        :returns: text of email

        """
        return self.__text

    @text.setter
    def text(self, txt):
        """Set text of email

        :param str txt:

        """
        self.__text = txt

    @property
    def serialized(self):
        """Serialized message

        :returns: dict of message members

        """
        message = dict()
        message['subject'] = self.subject
        message['sender'] = self.sender
        message['destination'] = self.destination
        message['body'] = self.body
        message['text'] = self.text
        message['header'] = self.header

        return message


class MailServer:
    """Mail Server

    """
    def __init__(self):
        self.__address = config.MAIL_SERVER
        self.__port = config.MAIL_PORT
        self.__user = config.MAIL_USERNAME
        self.__password = config.MAIL_PASSWORD
        self.__use_tls = config.MAIL_USE_TLS
        self.__use_ssl = config.MAIL_USE_SSL

        with Database() as db:
            mail_svr = db.session.query(Settings) \
                .join(SettingsValues, Settings.id_settings == SettingsValues.settings_id_settings) \
                .filter(and_(Settings.settings_group_name == 'RULES', Settings.settings_name.like('MAIL%'))) \
                .with_entities(Settings.settings_name, Settings.units, SettingsValues.value) \
                .all()
            if mail_svr is not None:
                mail_settings = dict()

                for setting in mail_svr:
                    if setting[1] == 'integer':
                        value = int(setting[2])
                    elif setting[1] == 'boolean':
                        value = True if setting[2] == 'ENABLED' else False
                    else:
                        value = setting[2]

                    mail_settings[setting[0]] = value

                self.__address = mail_settings['MAIL_SERVER']
                self.__port = mail_settings['MAIL_PORT']
                self.__user = mail_settings['MAIL_USERNAME']
                self.__password = mail_settings['MAIL_PASSWORD']
                self.__use_ssl = mail_settings['MAIL_USE_SSL']
                self.__use_tls = mail_settings['MAIL_USE_TLS']

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, addr):
        self.__address = addr

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port_num):
        self.__port = port_num

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user_acct):
        self.__user = user_acct

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, passwrd):
        self.__password = passwrd

    @property
    def use_ssl(self):
        return self.__use_ssl

    @use_ssl.setter
    def use_ssl(self, enable_ssl):
        self.__use_ssl = enable_ssl

    @property
    def use_tls(self):
        return self.__use_tls

    @use_tls.setter
    def use_tls(self, enable_tls):
        self.__use_tls = enable_tls

    @property
    def serialized(self):
        server = dict()
        server['address'] = self.address
        server['port'] = self.port
        server['user'] = self.user
        server['password'] = self.password
        server['use_ssl'] = self.use_ssl
        server['use_tls'] = self.use_tls
        return server
