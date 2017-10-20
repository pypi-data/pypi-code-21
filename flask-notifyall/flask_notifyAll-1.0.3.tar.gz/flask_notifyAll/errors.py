_twilio_cred_msg = """\
You don't add Twilio credentials into your config file or object
"""


class TwilioCredentialError(Exception):
    """
    Twilio Credentials Error class
    """
    def __str__(self):
        return _twilio_cred_msg


class FlaskNotifyEmailError(Exception):
    """
    Flask Notify email error class
    """
    pass


class FlaskNotifyAuthenticationError(Exception):
    """
    Flask Notify Authentication error class
    """
    def __str__(self):
        return 'Mailtrap SMTP credentials are wrong'
