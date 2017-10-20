import smtplib
from email.mime.text import MIMEText
from smtplib import SMTPAuthenticationError

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from .errors import (FlaskNotifyAuthenticationError, FlaskNotifyEmailError,
                     TwilioCredentialError)


class FlaskNotify:
    """Main class for the notification actions
        Variables:
            _config Dictionary with application credentials

        Functions:
            init_app Initialize and update _config object with credentials
            send_sms_notification Sends an sms on user cell phone
            send_verification_code Sends an sms on user cell phone with verification code
            send_mailtrap_email Sends email via Mailtrap SMTP
    """
    _config = {}

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        :param app: An Flask application
        """
        self._config.update(twilio_sid=app.config.get('TWILIO_SID'),
                            twilio_token=app.config.get('TWILIO_TOKEN'),
                            twilio_number=app.config.get('TWILIO_NUMBER'),
                            test_email=app.config.get('TEST_EMAIL'),
                            mailtrap_user=app.config.get('MAILTRAP_USER'),
                            mailtrap_pass=app.config.get('MAILTRAP_PASSWORD'))

    def send_sms_notification(self, to_user, message):
        """
        :param to_user: User which will get an sms notification
        :param message: Body of message
        """
        try:
            client = Client(
                self._config.get('twilio_sid'),
                self._config.get('twilio_token')
            )
        except TwilioException:
            raise TwilioCredentialError

        client.messages.create(from_=self._config.get('twilio_number'),
                               to=to_user,
                               body=message)

    def send_verification_code(self, to_user, verification_code):
        """
        :param to_user: User which will get an sms notification
        :param verification_code: Some random code
        """
        self.send_sms_notification(
            to_user=to_user,
            message='Your verifications code is {}'.format(verification_code)
        )
        return verification_code

    def send_mailtrap_email(self, emails, subject, body, email_port=2525):
        """
        :param emails: An list with email of users
        :param subject: Subject of email
        :param body: Body of email
        :param email_port: Port of email
        """
        if not isinstance(emails, list):
            raise FlaskNotifyEmailError('emails must be an list')

        user_name = self._config.get('mailtrap_user')
        password = self._config.get('mailtrap_pass')
        test_email = self._config.get('test_email')

        try:
            mail = smtplib.SMTP('smtp.mailtrap.io', email_port)
            mail.login(user_name, password)
        except SMTPAuthenticationError:
            raise FlaskNotifyAuthenticationError

        for email in emails:
            message = MIMEText(body)
            message['Subject'] = subject

            message['From'] = test_email

            message['To'] = email
            mail.sendmail(test_email, email, message.as_string())

        mail.quit()
