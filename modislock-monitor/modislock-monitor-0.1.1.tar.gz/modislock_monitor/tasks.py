# Async worker
from celery import Celery

# Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
from .config import load_config

# System calls
from subprocess import PIPE, Popen, run

config = load_config()
app = Celery('modis-mon', broker=config.CELERY_BROKER_URL)


@app.task
def reboot():
    args = ['systemctl', 'reboot']
    ret = run(args, timeout=60)


@app.task
def system_reset():
    sql_statement = "UPDATE settings_values SET value='ENABLED' " \
                    "WHERE settings_id_settings = (SELECT settings.id_settings " \
                    "FROM settings WHERE settings.settings_name = 'REGISTRATION');"
    args = ['mysql', '-u', 'root', '-D', 'modislock']

    p = Popen(args, stdin=PIPE, stdout=PIPE)
    out, err = p.communicate(sql_statement.encode(), timeout=30)
    print(out, err)
    args = ['supervisorctl', 'restart', 'admin:modis_admin']
    ret = run(args, timeout=60)


@app.task
def factory_reset():
    args = ['mysql', '-u', 'root', '-D', 'modislock']

    p = Popen(args, stdin=PIPE, stdout=PIPE)
    out, err = p.communicate('SOURCE /etc/modis/modislock_init.sql;\nexit\n'.encode(), timeout=30)
    print(out, err)
    args = ['systemctl', 'reboot']
    ret = run(args, timeout=60)


@app.task
def send_async_msg(message, server):
    """
    Send a message using SMTP
    :param from_address:
    :param kwargs:
    :return:
    """
    # Create a Container
    msg = MIMEMultipart()
    msg['Subject'] = message.subject
    msg['From'] = message.sender
    msg['To'] = message.destination
    msg.preamble = message.header

    # Add body
    body = MIMEText(message.body, 'html')
    msg.attach(body)

    send = smtplib.SMTP(server.address, server.port)
    # Add ttls
    send.ehlo()
    # Login
    send.login(server.user, server.password)
    # Send
    send.send_message(msg)
    # Quit
    send.quit()


__all__ = ['app', 'send_async_msg', 'reboot', 'system_reset', 'factory_reset']
