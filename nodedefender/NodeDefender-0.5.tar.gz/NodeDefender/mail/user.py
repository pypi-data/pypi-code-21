from flask_mail import Message
from flask import render_template, url_for
import NodeDefender
from NodeDefender import serializer
from NodeDefender.mail import mail
import smtplib

@NodeDefender.decorators.mail_enabled
@NodeDefender.decorators.celery_task
def new_user(user):
    if type(user) == str:
        user = NodeDefender.db.user.get(user)

    if user.email == None:
        return False
    msg = Message('Welcome to NodeDefender', sender='noreply@nodedefender.com',
                  recipients=[user.email])
    url = url_for('auth_view.register_token',\
                  token = serializer.dumps_salted(user.email))
    msg.body = render_template('mail/user/create_user.txt', user = user, url =
                              url)
    try:
        mail.send(msg)
    except smtplib.SMTPRecipientsRefused:
        NodeDefender.mail.logger.error("Unable to send email to: {}".\
                                format(user.email))
    except smtplib.SMTPAuthenticationError:
        NodeDefender.mail.logger.error("Authentication error when sending Email")
    return True

@NodeDefender.decorators.mail_enabled
@NodeDefender.decorators.celery_task
def confirm_user(user):
    if type(user) == str:
        user = NodeDefender.db.user.get(user)

    if user.email == None:
        return False

    msg = Message('Confirm Successful!', sender='noreply@nodedefender.com',
                  recipients=[user.email])
    msg.body = render_template('mail/user/user_confirmed.txt', user = user)
    try:
        mail.send(msg)
    except smtplib.SMTPRecipientsRefused:
        NodeDefender.mail.logger.error("Unable to send email to: {}".\
                                format(user.email))
    except smtplib.SMTPAuthenticationError:
        NodeDefender.mail.logger.error("Authentication error when sending Email")
    return True

@NodeDefender.decorators.mail_enabled
@NodeDefender.decorators.celery_task
def reset_password(user):
    if type(user) == str:
        user = NodeDefender.db.user.get(user)

    if user.email == None:
        return False

    msg = Message('Reset password', sender='noreply@nodedefender.com',
                  recipients=[user.email])
    url = url_for('auth_view.reset_password',\
                 token = serializer.dumps_salted(user.email))
    msg.body = render_template('mail/user/reset_password.txt', user = user, url =
                              url)
    try:
        mail.send(msg)
    except smtplib.SMTPRecipientsRefused:
        NodeDefender.mail.logger.error("Unable to send email to: {}".\
                                format(user.email))
    except smtplib.SMTPAuthenticationError:
        NodeDefender.mail.logger.error("Authentication error when sending Email")
    return True

@NodeDefender.decorators.mail_enabled
@NodeDefender.decorators.celery_task
def login_changed(user):
    if type(user) == str:
        user = NodeDefender.db.user.get(user)
    
    msg = Message('Login changed', sender='noreply@nodedefender.com',
                  recipients=[user.email])
    msg.body = render_template('mail/user/reset_password.txt', user = user)
    try:
        mail.send(msg)
    except smtplib.SMTPRecipientsRefused:
        NodeDefender.mail.logger.error("Unable to send email to: {}".\
                                format(user.email))
    except smtplib.SMTPAuthenticationError:
        NodeDefender.mail.logger.error("Authentication error when sending Email")
    return True
