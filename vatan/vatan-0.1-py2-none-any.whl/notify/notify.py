import smtplib
import io
import os
import pkg_resources
from vatan import config
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# TODO secure password securely
email_store = config.main_dir + '.mailpass'


def send_mail(item, snapshot):
    email, pw = get_user_email_details()
    print 'Notifying %s, %s' % (email, pw)
    server = smtplib.SMTP(host='smtp.gmail.com', port='587')
    server.ehlo()
    server.starttls()
    server.login(email, pw)
    mime_msg = MIMEMultipart()
    mime_msg['From'] = email
    mime_msg['To'] = email
    mime_msg['Subject'] = 'vatan.py: Price has changed!'
    mime_msg.attach(MIMEText(
                            prepare_content(snapshot.name,
                                            item.amount, snapshot.amount, item.currency)))
    server.sendmail(email, email, mime_msg.as_string())
    server.close()


def prepare_content(item_name, price, last_price, currency):
    t = read_template()
    return t.substitute(ITEM=item_name.encode('UTF-8'), PRICE=price,
                        LAST_PRICE=last_price, CURR=currency.encode('UTF-8'))


def read_template():
    content = pkg_resources.resource_string('vatan.resources', 'mail')
    return Template(content)


def store_user_email():
    import getpass
    email = raw_input('Enter your e-mail to get notified: ')
    pw = getpass.getpass('Enter e-mail password: ')
    with io.open(email_store, 'wt', encoding='UTF-8', newline=None) as f:
        ser = ':'.join((unicode(email), unicode(pw)))
        f.write(ser + os.linesep)


def get_user_email_details():
    with io.open(email_store, 'rt', encoding='UTF-8', newline=None) as f:
        return f.readline().rstrip(os.linesep).split(':')
