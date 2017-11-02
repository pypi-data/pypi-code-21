from django.core.mail import send_mail
from smtplib import SMTPException
import logging

logger = logging.getLogger(__name__)


def send(from_email=None, to_emails=None, subject='Apollo Email', content=None):
    """ send an
    """
    if from_email is None:
        raise AttributeError('a from_email must be set to send mail')
    elif not to_emails:
        raise AttributeError('to_emails must be set to send mail')

    logger.debug('sending email now')

    try:
        send_mail(subject, content, from_email, to_emails, fail_silently=False)
    except SMTPException as exc:
        logger.error('error sending email from %s to %s (exc: %s)' % (from_email, to_emails, str(exc)))
        return False

    return True