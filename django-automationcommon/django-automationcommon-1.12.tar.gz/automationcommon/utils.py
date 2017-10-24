import datetime
import logging
import re
from celery import Task
from celery import shared_task
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.template import Context
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from stronghold.decorators import public
from ucamlookup import createConnection, PersonMethods


LOGGER = logging.getLogger('automationcommon')


class ApplicationError(Exception):
    """
    This class is intended as a base class for all application errors.
    """
    pass


def get_users_email_address_from_lookup(user, email_only=False):
    """
    This function look's up an email address for a user. If one cannot be found it returns a default
    of crsid@cam.ac.uk.

    :param user: django user
    :param email_only: True = '{email}' False = '{name} <{email}>'
    :return: looked up user email of default
    """
    conn = createConnection()
    result = PersonMethods(conn).getPerson(scheme="crsid", identifier=user.username, fetch="email")
    if user.get_full_name() and not email_only:
        default = "%s <%s@cam.ac.uk>" % (user.get_full_name(), user.username)
    else:
        default = "%s@cam.ac.uk" % user.username
    if result is None:
        LOGGER.info("no results returned from email lookup - defaulting to '%s'" % default)
        return default
    if result.attributes is None or len(result.attributes) == 0:
        LOGGER.warning("no attributes returned from email lookup - defaulting to '%s'" % default)
        return default
    if '@' not in result.attributes[0].value:
        LOGGER.warning("'%s' is not an email address - defaulting to '%s'" % (result.attributes[0].value, default))
        return default
    if user.get_full_name() and not email_only:
        return "%s <%s>" % (user.get_full_name(), result.attributes[0].value)
    return result.attributes[0].value


class TaskWithFailure(Task):
    """
    Abstract celery Task that logs failure.
    """
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        LOGGER.error("An error happened (%s) when trying to execute celery task with id %s and arguments %s and %s\n\n"
                     "The traceback is:\n%s\n", exc, task_id, args, kwargs, einfo)


class ProtectedView(TemplateView):
    """
    A abstract TemplateView to extend from that requires login.
    """
    abstract = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)


class PublicView(TemplateView):
    """
    A abstract TemplateView to extend from that is stronghold public.
    """
    abstract = True

    @method_decorator(public)
    def dispatch(self, *args, **kwargs):
        return super(PublicView, self).dispatch(*args, **kwargs)


@shared_task(base=TaskWithFailure)
def test_celery_email():
    """
    This function is used to test the logging and exception handling functionality of celery
    """
    LOGGER.info("This is a test Celery info log")
    LOGGER.warning("This is a test Celery warning log")
    LOGGER.error("This is a test Celery error log")
    raise Exception("This is test for a Celery Exception")


def simple_authorization(func):
    """
    Decorator to test an HTTP request for an authorization header with a matching .
    """
    def func_wrapper(*argv, **kwargs):

        request = argv[0]

        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('Unauthorized', status=401)

        parts = request.META['HTTP_AUTHORIZATION'].split(" ")
        if len(parts) != 2 or parts[0].lower() != 'bearer' or parts[1] != settings.SSGW_API_TOKEN:
            return HttpResponse('Unauthorized', status=401)

        return func(*argv, **kwargs)

    return func_wrapper


def paginate(request, object_list, per_page=25):
    """
    Helper method for django Paginator - assumes a request parameter of "page".

    :param request: http request
    :param object_list: sourse to select page from
    :param per_page: the number of objects per page
    :return: Paginator page
    """
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page')
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        return paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)


def send(recipients, email_template, context, attachments=None, reply_to=None, bcc=False, **kwargs):
    """
    Sends an email. By convention the first line of the template is assumed to be the subject.

    :param recipients: either list of recipients or single recipient -
                       each receipient is either an email string or a User
    :param email_template: the email template
    :param context: context for the email template
    :param attachments: optional attachments (assumes either one of the other)
    :param reply_to: optional "reply to" address
    :param bcc: if True then bcc to SERVER_EMAIL

    :return: the sent EmailMessage
    """
    template = get_template('email/' + email_template + '.txt')
    subject_and_body = template.render(Context(context)).split('\n', 1)
    if isinstance(recipients, str) or isinstance(recipients, User):
        recipients = [recipients]

    to = [recipient if isinstance(recipient, str) else get_users_email_address_from_lookup(recipient)
          for recipient in recipients]

    if reply_to:
        if reply_to.__class__ == list:
            kwargs['reply_to'] = reply_to
        else:
            kwargs['reply_to'] = [reply_to]

    if bcc:
        kwargs['bcc'] = [settings.SERVER_EMAIL]

    final_kwargs = {**{
        'subject': subject_and_body[0],
        'body': subject_and_body[1],
        'from_email': settings.SERVER_EMAIL_FULL,
        'to': to,
        'headers': {'Return-Path': settings.SERVER_EMAIL}
    }, **kwargs}

    message = EmailMultiAlternatives(**final_kwargs)

    try:
        template = get_template('email/' + email_template + '.html')
        message.attach_alternative(template.render(Context(context)), "text/html")
    except TemplateDoesNotExist:
        pass

    if attachments:
        if attachments.__class__ != list:
            attachments = [attachments]
        for attachment in attachments:
            if attachment.__class__ == tuple:
                message.attachments.append(attachment)
            else:
                message.attach(attachment.name, attachment.read())

    message.send()
    LOGGER.info("email sent: to='%s' template='%s' context=%s" % (to, email_template, context))

    return message


def merge_dicts(dict1, dict2):
    """
    Merge 2 dictionaries.
    """
    merged = dict1.copy()
    merged.update(dict2)
    return merged


def json_date_parser(json_dict):
    """
    Used to convert dates when de-serialising JSON. Looks for keys containing the string "DATE" and tries to convert
    their value to a datetime.

    Usage: json.loads(x, object_hook=json_date_parser)

    :param json_dict: dict loaded from JSON.
    :return: json_dict
    """
    for k, v in json_dict.items():
        if isinstance(v, str) and re.search("DATE", k):
            try:
                json_dict[k] = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
    return json_dict


def json_date_formatter(obj):
    """
    Used to format datetimes when serialising JSON.

    Usage: json.dumps(x, default=json_date_formatter)

    :param obj: object to serialise
    :return: serialised object
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError
