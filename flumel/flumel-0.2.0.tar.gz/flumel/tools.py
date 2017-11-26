"""
Boite à outils
"""
import imaplib
import smtplib
from email import message_from_bytes
from email.header import decode_header, make_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text
import pkg_resources

from . import settings


def sendmail(recipient, subject, html, **kwargs):
    """
    Envoi d'un email multipart
    Le corps du message est envoyé en html et sa conversion en texte brut par html2text
    Les kwargs permettent de personnaliser les entêtes du mail X-Flumel
    par ex. Title="Test" -> X-Flumel-Title = "Test"
    """
    server = SMTP()
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = settings.BOT_EMAIL
    message['To'] = recipient
    if kwargs:
        for key, value in kwargs.items():
            message['X-Flumel-' + key] = value

    text = html2text.html2text(html)
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    server.sendmail([recipient], message.as_string())
    server.close()


def format_template(name, **kwargs):
    """
    `format` le contenu du template `name` avec kwargs
    pkg_resources.resource_string est utilisé pour récupérer le path de flumel
    """
    path = '/'.join(['templates', name])
    html = pkg_resources.resource_string(__name__, path).decode("utf-8")
    return html.format(**kwargs)


def decode_email_header(value):
    """
    Les headers des emails sont encodés comme des sagouins
    https://docs.python.org/3/library/email.header.html#email.header.decode_header
    @see https://stackoverflow.com/a/12071098

    """
    return str(make_header(decode_header(value))).strip()


class IMAP:
    """
    Interface simplifiée pour imaplib.IMAP4
    La connexion est en SSL si BOT_IMAP_PORT == 993, sinon c'est en starttls
    """

    server = None

    def __init__(self):
        """
        Connexion + login
        """
        if settings.BOT_IMAP_PORT == 993:
            self.server = imaplib.IMAP4_SSL(settings.BOT_IMAP_HOST)
        else:
            self.server = imaplib.IMAP4(settings.BOT_IMAP_HOST)
            self.server.starttls()
        self.server.login(settings.BOT_LOGIN, settings.BOT_PASSWORD)

    def __repr__(self):
        """
        L’objet IMAP4
        """
        return self.server

    @property
    def inbox(self):
        """
        Récupération de la liste des messages dans l’inbox, retourne un tableau iterable
        """
        self.server.select()  # ouverture inbox
        _, listing = self.server.search(None, 'ALL')  # (résultat, list)
        return listing[0].split()

    def get(self, number):
        """
        Retourne le message `number`
        """
        _, msg = self.server.fetch(number, '(RFC822)')  # (résultat, message)
        return message_from_bytes(msg[0][1])

    def delete(self, number):
        """
        Flag le message `number` à supprimer
        """
        return self.server.store(number, '+FLAGS', '\\Deleted')

    def purge(self):
        """
        Vide l’inbox après avoir marqué l’ensemble des messages à supprimer
        """
        for number in self.inbox:
            self.delete(number)
        return self.server.expunge()

    def close(self):
        """
        Efface les messages avec flag et clôture la connexion
        """
        self.server.select()  # command EXPUNGE only allowed in states SELECTED
        self.server.expunge()
        self.server.close()
        self.server.logout()


class SMTP:
    """
    Interface simplifiée pour smtplib.SMTP
    La connexion est en SSL si BOT_SMTP_PORT == 465, sinon c'est en starttls
    """

    server = None

    def __init__(self):
        """
        Connexion & login
        """
        if settings.BOT_SMTP_PORT == 465:
            self.server = smtplib.SMTP_SSL(settings.BOT_SMTP_HOST,
                                           settings.BOT_SMTP_PORT)
        else:
            self.server = smtplib.SMTP(settings.BOT_SMTP_HOST,
                                       settings.BOT_SMTP_PORT)
            if settings.BOT_SMTP_PORT == 587:
                self.server.starttls()
        try:
            self.server.login(settings.BOT_LOGIN, settings.BOT_PASSWORD)
        except smtplib.SMTPNotSupportedError:
            pass

    def __repr__(self):
        """
        L’objet SMTP
        """
        return self.server

    def sendmail(self, recipients, message):
        """
        Envoi du message
        """
        return self.server.sendmail(settings.BOT_EMAIL, recipients, message)

    def close(self):
        """
        Clôture de la connexion
        """
        self.server.quit()
