import os
import os.path as path
from configparser import ConfigParser
from collections import namedtuple
import smtplib
from email.mime.text import MIMEText
from .decorators import validate_method_args


SmtpCreds = namedtuple('SmtpCreds', ['host', 'port', 'email', 'password'])

SMS_GATEWAYS = {
    'att': 'mms.att.net',
    't-mobile': 'tmomail.net',
    'verizon': 'vtext.com',
    'sprint': 'page.nextel.com'
}


class Messenger:
    def __init__(self, smtp_creds=None):
        if not smtp_creds:
            smtp_creds = self._load_creds_from_env()
        if not smtp_creds:
            smtp_creds = self._load_creds_from_file()
        if not smtp_creds:
            msg = 'Missing smtp creds! Refer to https://bitbucket.org/avilay/utils#smtp_creds on how to set SMTP creds.'
            raise RuntimeError(msg)
        self._smtp_creds = smtp_creds

        self._conn = None

    def _load_creds_from_env(self):
        creds = []
        for var in ['SMTP_HOST', 'SMTP_PORT', 'SMTP_EMAIL', 'SMTP_PASSWORD']:
            creds.append(os.environ.get(var, None))
        if None in creds:
            return None
        else:
            return SmtpCreds(host=creds[0], port=creds[1], email=creds[2], password=creds[3])

    def _load_creds_from_file(self):
        creds_file = path.expanduser(path.join('~', '.smtp_creds'))
        if path.exists(creds_file):
            config = ConfigParser()
            config.read(creds_file)
            creds = []
            for name in ['host', 'port', 'email', 'password']:
                creds.append(config.get('SMTP', name, fallback=None))
            if None in creds:
                return None
            else:
                return SmtpCreds(host=creds[0], port=creds[1], email=creds[2], password=creds[3])
        else:
            return None

    def _connect(self):
        self._conn = smtplib.SMTP(self._smtp_creds.host, self._smtp_creds.port)
        self._conn.starttls()
        self._conn.login(self._smtp_creds.email, self._smtp_creds.password)

    def _close(self):
        self._conn.quit()
        self._conn = None

    @validate_method_args([
        ('number', int, lambda x: x > 1000000000),
        ('carrier', str, lambda x: x in SMS_GATEWAYS),
        ('msg', str, lambda x: x)
    ])
    def text(self, number, carrier, msg):
        self._connect()
        sms_gateway = '{}@{}'.format(number, SMS_GATEWAYS[carrier])
        self._conn.sendmail(self._smtp_creds.email, sms_gateway, msg)
        self._close()

    @validate_method_args([
        ('to', str, lambda x: x.find('@') > -1),
        ('sub', str, None),
        ('msg', str, lambda x: x)
    ])
    def email(self, to, sub, msg):
        self._connect()
        message = MIMEText(msg)
        message['Subject'] = sub
        message['From'] = self._smtp_creds.email
        message['To'] = to
        self._conn.send_message(message)
        self._close()
