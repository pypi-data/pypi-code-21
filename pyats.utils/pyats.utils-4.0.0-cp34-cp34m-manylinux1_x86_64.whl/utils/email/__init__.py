import os
import logging
import smtplib

from email.message import EmailMessage
from email.headerregistry import Address
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# internal Cisco SMTP information
DOMAIN = 'cisco.com'
SMTP_HOST = 'mail.cisco.com'


class EmailMsg(object):
    '''EmailMsg Class

    A container for email information.

    '''

    def __init__(self,
                 from_email = None,
                 to_email = None,
                 subject = '',
                 body = '',
                 attachments = None,
                 html_email = False,
                 html_body = '',
                 default_email_domain = DOMAIN,
                 smtp_host = SMTP_HOST,
                 smtp_port = '25',
                 smtp_username = None,
                 smtp_password = None):
        '''EmailMsg constructor
        Initialize a single email message (which can be sent to multiple
        recipients).

        Arguments
        ---------
            from_email (list/str): list or string-list of addresses to be used
                                   in the generated email's "From:" field.
            to_email(list/str): list or string-list of addresses to be used
                                in the generated email's "To:" field.
            subject (str): alternate subject for the report email
            body (string): message body in the email
            attachments (list): list of attachments paths
            html_email (bool): flag to enable alternative email format
            html_body (string): html content

        '''
        # convert email addresses into Address objects
        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.html_email = html_email
        self.html_body = html_body
        self.default_email_domain = default_email_domain
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    @staticmethod
    def convert_to_address(value, default_domain):
        '''convert address values

        converts space/comma/semi-colon delimited strings and lists of string
        ids into email address objects.
        '''
        if isinstance(value, str):
            value = value.replace(',', ' ')
            value = value.replace(';', ' ')
            value = value.split()

        addresses = []
        for item in value:
            if '@' in item:
                name, domain = item.split('@')
                addresses.append(Address(username = name, domain = domain))
            elif default_domain:
                addresses.append(Address(username = item, 
                                         domain = default_domain))
            else:
                raise ValueError("Please specify default email domain, or "
                                 "provide the full email address")

        return addresses

    def message(self):
        '''creates message

        Constructs email.message.EmailMessage object

        Return
        ------
            msg - email.message.EmailMessage object
        '''

        msg = EmailMessage()
        msg['From'] = self.convert_to_address(self.from_email,
                                              self.default_email_domain)
        msg['To'] = self.convert_to_address(self.to_email,
                                            self.default_email_domain)
        msg['Subject'] = self.subject
        msg.set_content(self.body)

        # should this email be sent in html?
        if self.html_email:
            msg.add_alternative(self.html_body, subtype = 'html')

        # any attachments that need to be enclosed?
        if self.attachments:
            for attachment in self.attachments:
                try:
                    with open(attachment) as fp:
                        attach = MIMEText(fp.read())
                        fp.close()

                        msg.add_attachment(
                            attach,
                            filename=os.path.basename(attachment)
                        )
                except FileNotFoundError as err:
                    logger.warning('%s - email will be sent with no '
                                   'attachment.' % err)

        return msg

    def get_content(self):
        '''get message body

        Returns report plain text body

        Return
        ------
            self.body
        '''
        return self.body

    def recipients(self):
        '''recipients list

        Returns a list of all recipients of the email

        Return
        ------
            self.to_email
        '''
        return self.to_email

    def send(self, smtp_host = None, 
                   smtp_port = None, 
                   smtp_username = None, 
                   smtp_password = None):
        '''send message

        Sends email using mail.cisco.com host

        '''

        if not self.recipients():
            raise ValueError('Recipient list is empty.')

        host = smtp_host or self.smtp_host
        port = smtp_port or self.smtp_port
        username = smtp_username or self.smtp_username
        password = smtp_password or self.smtp_password

        logger.debug('Sending messaging to %s:%s' % (host, port))

        # send the bloody email
        with smtplib.SMTP(host = host, port = port) as smtp:
            if username and password:
                smtp.login(username, password)
            smtp.send_message(self.message())

    @property
    def mailbody(self):
        '''mailbody property getter

        Returns the body attribute of EmailMsg object.
        '''
        return self.body

    @mailbody.setter
    def mailbody(self, body):
        '''mailbody property setter
        Allows modification of mail body in EmailMsg object.
        '''
        self.body = body

    @property
    def mailsubject(self):
        '''mailsubject property getter

        Returns the subject attribute of EmailMsg object.
        '''
        return self.subject

    @mailsubject.setter
    def mailsubject(self, subject):
        '''mailsubject property setter
        Allows modification of mail subject in EmailMsg object.
        '''
        self.subject = subject


