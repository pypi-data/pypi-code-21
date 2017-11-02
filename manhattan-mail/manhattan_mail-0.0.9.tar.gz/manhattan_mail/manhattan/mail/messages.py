from email import charset, encoders
from email.header import Header
from email.headerregistry import Address
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
import mimetypes
import os
import re
import socket

import html2text
from jinja2 import Environment, FileSystemLoader
from premailer import Premailer

__all__ = [
    'EmailAttachment',
    'EmailContact',
    'EmailMessage',
    'EmailTemplate'
    ]

# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
utf8_charset = charset.Charset('utf-8')
utf8_charset.body_encoding = None
utf8_charset_qp = charset.Charset('utf-8')
utf8_charset_qp.body_encoding = charset.QP

# Patch mimetypes lib to recognize CSV files
mimetypes.add_type('text/csv', '.csv')


class EmailAttachment:
    """
    Information about an email attachment.
    """

    BASETYPE_MAP = {
        'application': MIMEApplication,
        'audio': MIMEAudio,
        'image': MIMEImage,
        'text': MIMEText
    }
    DEFAULT_MIMETYPE = 'application/octet-stream'

    def __init__(self, filename, content, mimetype=None):
        self.filename = filename
        self.content = content

        # Determine the mimetype
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = self.DEFAULT_MIMETYPE

        self.mimetype = mimetype

        # If the base type is text check that the content isn't binary
        basetype, subtype = self.mimetype.split('/', 1)

        if basetype == 'text':
            if isinstance(self.content, bytes):
                try:
                    self.content = self.content.decode()
                except UnicodeDecodeError:
                    self.mimetype = self.DEFAULT_MIMETYPE

    @property
    def attachment(self):
        """Return an email attachment"""
        attachment = None

        # Build the MIME object
        basetype, subtype = self.mimetype.split('/', 1)
        if basetype in self.BASETYPE_MAP:
            attachment = self.BASETYPE_MAP[basetype](self.content, subtype)
        else:
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(self.content)
            encoders.encode_base64(attachment)

        # Set the filename
        attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=self.filename
            )

        return attachment

    @classmethod
    def from_file(cls, file_path):
        """Create an attachment from a file"""
        filename = None
        content = None

        if isinstance(file_path, str):
            filename = file_path
            with open(file_path, 'rb') as f:
                content = f.read()

        else:
            filename = file_path.name
            file_path.seek(0)
            content = file_path.read()

        return cls(os.path.basename(filename), content)


class EmailContact:
    """
    Information about a email recipient or sender.
    """

    def __init__(self, addr, name='', encoding='utf-8'):
        self.addr = addr
        self.name = name
        self.encoding = encoding

    def __eq__(self, other):
        return self.addr == other.addr

    def __hash__(self):
        return hash(self.addr)

    def __iter__(self):
        for v in (self.addr, self.name, self.encoding):
            yield v

    def __repr__(self):
        return str(self)

    def __str__(self):
        """Return an email contact"""
        username, domain = self.addr.split('@', 1)
        try:
            username.encode('ascii')
        except UnicodeEncodeError:
            username = Header(username, self.encoding).encode()
        domain = domain.encode('idna').decode('ascii')
        addr = Address(self.name, username=username, domain=domain)
        return str(addr)

    @classmethod
    def normalize(cls, addrs, default_encoding='utf-8'):
        """
        Normalize one or more addresses of the form string, tuple or
        `EmailContact`) to `EmailContact`s.
        """
        normalized = []
        for addr in addrs:
            if isinstance(addr, cls):
                addr = addr
            elif isinstance(addr, tuple):
                addr = cls(*addr)
            else:
                addr = cls(addr)
            normalized.append(addr)
        return normalized


class EmailMessage:
    """
    Information about an email message.
    """

    LINE_LENGTH_LIMIT = 998

    def __init__(
            self,
            to,
            sender,
            subject,
            body_text=None,
            body_html=None,
            cc=None,
            bcc=None,
            attachments=None,
            headers=None,
            encoding='utf-8'
            ):

        # A list of recipients for the email
        self.to = EmailContact.normalize(to)

        # A list of contacts who will be CC'd on this email
        self.cc = EmailContact.normalize(cc or [])

        # A list of contacts who will be bCC'd on this email
        self.bcc = EmailContact.normalize(bcc or [])

        # The contact the email is being sent from
        self.sender = EmailContact.normalize([sender])[0]

        # The subject line for the email
        self.subject = subject

        # The body of the email in plain text format
        self.body_text = body_text

        # The body of the email in HTML format
        self.body_html = body_html

        # If a plain text body hasn't been provided then create one
        if self.body_text is None and self.body_html:
            text_maker = html2text.HTML2Text()
            self.body_text = text_maker.handle(self.body_html)

        # A list of attachments to be attached to the message
        self.attachments = attachments or []

        # A list of additional headers for the message
        self.headers = headers or {}

        # The charet encoding for the body of the email
        self.encoding = encoding

    def attach(self, attachment):
        """
        Add an attachment to the email message, the attachment can be an
        `EmailAttachment` instance, a file point or file path.
        """
        if isinstance(attachment, EmailAttachment):
            self.attachments.append(attachment)
        else:
            attachment = EmailAttachment.from_file(attachment)
            self.attachments.append(attachment)
        return attachment

    @property
    def message(self):
        """Return an email message"""

        # Build the text message
        msg = text_msg = self._safe_mime_text(
            self.body_text,
            'plain',
            self.encoding
            )

        # Build the HTML message
        if self.body_html:
            html_msg = self._safe_mime_text(
                self.body_html,
                'html',
                self.encoding
                )

        # Handle attachments
        if len(self.attachments):
            msg = MIMEMultipart(_subtype='mixed', encoding=self.encoding)

            # If a HTML version of the email is provided then we need to create
            # a text and HTML message to attach to the primary message along
            # with the attachments...
            if self.body_html:
                text_html_msg = MIMEMultipart(
                    _subtype='alternative',
                    encoding=self.encoding
                    )
                text_html_msg.attach(text_msg)
                text_html_msg.attach(html_msg)
                msg.attach(text_html_msg)

            # ...else we simple attact the text.
            else:
                msg.attach(text_msg)

            # Add any attachments
            for attachment in self.attachments:
                msg.attach(attachment.attachment)

        elif self.body_html:
            # If a HTML version is provided then we need to create a text and
            # HTML message as the primary message.
            msg = MIMEMultipart(_subtype='alternative', encoding=self.encoding)
            msg.attach(text_msg)
            msg.attach(html_msg)

        # Add common headers
        msg['Subject'] = self.subject
        msg['From'] = str(self.sender)
        msg['To'] = ', '.join([str(r) for r in self.to])
        if self.cc:
            msg['Cc'] = ', '.join([str(r) for r in self.cc])
        msg['Date'] = formatdate()
        msg['Message-ID'] = make_msgid(socket.getfqdn())

        # Add extra headers
        header_names = [k.lower() for k in self.headers]
        for name, value in self.headers.items():
            if name.lower() in ('from', 'to'):
                continue
            msg[name] = value

        return msg

    @property
    def recipients(self):
        """Return a list of all recipients for the email message"""
        return self.to + self.cc + self.bcc

    def _safe_mime_text(self, payload, subtype, charset):
        """Return a MIMEText message that is safe to send"""

        # Check for utf-8 encoding
        if charset == 'utf-8':
            charset = utf8_charset

            # Check for long lines
            has_long_lines = any(
                len(l.encode()) > self.LINE_LENGTH_LIMIT
                for l in payload.splitlines()
                )
            if has_long_lines:
                charset = utf8_charset_qp

        # Set the payload
        msg = MIMEText('', subtype)
        msg.set_payload(payload, charset=charset)

        return msg

class EmailTemplate:
    """
    A class for generating one or more `EmailMessage` by mail merging a template
    with a list of recipients.
    """

    def __init__(
            self,
            to,
            sender,
            subject,
            template_path,
            template_map=None,
            css='',
            recipient_vars=None,
            global_vars=None,
            cc=None,
            bcc=None,
            attachments=None,
            headers=None,
            base_url=None,
            format='html',
            encoding='utf-8'
            ):

        # A list of recipients for the email
        self.to = EmailContact.normalize(to)

        # A list of contacts who will be CC'd on this email
        self.cc = EmailContact.normalize(cc or [])

        # A list of contacts who will be bCC'd on this email
        self.bcc = EmailContact.normalize(bcc or [])

        # The contact the email is being sent from
        self.sender = EmailContact.normalize([sender])[0]

        # The subject for the email. The subject string is compiled as a
        # template and can therefore be personalized using recipient and global
        # vars.
        self.subject = subject

        # The path to the template
        self.template_path = template_path

        # Template maps allow the template (and the templates it depends on) to
        # be provided as strings (instead of relying on the file system).
        self.template_map = template_map

        # A string of CSS that that will be inlined into each email messages
        # HTML body (only relevant when the format is HTML).
        self.css = css

        # A dictionary of recipient data where each recipients data is stored
        # against the recipients email address, e.g:
        #
        #     {recipient email: {recipient data}}.
        #
        # When an email message is compiled for a recipient, the message
        # recipient's data is provided to the email template so that the message
        # and subject can be personalized.
        #
        self.recipient_vars = recipient_vars or {}

        # A dictionary of data provided to when compiling the template and
        # subject for all messages.
        self.global_vars = global_vars or {}

        # A list of attachments to attach to any email message generated by the
        # template.
        self.attachments = attachments or []

        # A list of headers to include in any email message generated by the
        # template.
        self.headers = headers or {}

        # The base URL to prefix to all relative URLs within the email
        self.base_url = base_url

        # The format the template will output email messages as (either 'html'
        # or 'text'). The default is 'html', however, at text alternative is
        # automatically generated for HTML email messages.
        self.format = format

        # The encoding used when the template outputs an email message
        self.encoding = encoding

    def attach(self, attachment):
        """
        Add an attachment to the email template, the attachment can be an
        `EmailAttachment` instance, a file point or file path.
        """
        if isinstance(attachment, EmailAttachment):
            self.attachments.append(attachment)
        else:
            attachment = EmailAttachment.from_file(attachment)
            self.attachments.append(attachment)
        return attachment

    def get_jinja_env(self):
        """
        Return an environment to render the template with (this method should
        be overridden if you want to provide a custom environment).
        """
        return Environment(
            loader=FileSystemLoader(''),
            autoescape=True
            )

    def inline_css(self, body, css):
        """
        Inline CSS into a body of HTML (this method should be overridden if you
        want to implement a custom CSS inliner).
        """
        premailer = Premailer(
            body,
            base_url=self.base_url,
            css_text=css,
            keep_style_tags=True,
            strip_important=False,
            include_star_selectors=True,
            disable_validation=True
            )
        return premailer.transform()

    def merge(self):
        """Generate a list of email messages from the template"""
        messages = []

        # Build the templates
        env = self.get_jinja_env()

        # Subject
        subject_template = env.from_string(self.subject)

        # Body

        # If a template map is provided use it to build the template
        # environment (render from memory).
        body_template = None
        if self.template_map:
            # Compile and store each template in the mapping accept the one
            # specified by the template path.
            templates = {}
            for name, template in self.template_map.items():
                if name == self.template_path:
                    continue
                templates[name] = env.from_string(template, templates)

            # Compile the email template
            body_template = env.from_string(
                self.template_map[self.template_path],
                templates
                )

        # ...else render the template from via the file system
        else:
            body_template = env.get_template(self.template_path)

        # Strip comments from the CSS before inlining it
        css = re.sub(r'(?s)/\*.*?\*/', '', self.css).strip()

        for recipient in self.to:

            # Build the template args
            template_args = {}
            template_args.update(self.global_vars)
            template_args.update(self.recipient_vars.get(recipient.addr, {}))

            # Render the subject
            subject = subject_template.render(**template_args)

            # Render the body
            body = body_template.render(**template_args)

            # Inline the CSS for the message
            if self.css and self.format == 'html':
                body = self.inline_css(body, css)

            # Create the message and add it to the list of mail merged messages
            messages.append(EmailMessage(
                to=[recipient],
                sender=self.sender,
                subject=subject,
                body_text=body if self.format == 'text' else None,
                body_html=body if self.format == 'html' else None,
                cc=self.cc,
                bcc=self.bcc,
                attachments=self.attachments,
                headers=self.headers,
                encoding=self.encoding
                ))

        return messages
