import logging

from functools import wraps

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.utils import header_keys_from_request_env
from tcell_agent.sanitize import SanitizeUtils
from tcell_agent.sensor_events import LoginEvent

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


# Easy test mocking
def get_logger():
    return LOGGER


def report_login_event(
        request_env,
        status,
        user_id,
        session_id,
        document_uri,
        user_agent=None,
        referrer=None,
        remote_address=None,
        header_keys=None):

    login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
    if login_policy is None or not login_policy.is_enabled:
        return

    from tcell_hooks.v1 import LOGIN_SUCCESS, LOGIN_FAILURE

    if user_agent is None:
        user_agent = request_env.get("HTTP_USER_AGENT")
    if referrer is None:
        referrer = request_env.get("HTTP_REFERER")
    if header_keys is None:
        header_keys = header_keys_from_request_env(request_env)
    if remote_address is None and request_env != {}:
        remote_address = better_ip_address(request_env)

    if session_id is not None:
        session_id = SanitizeUtils.hmac_half(session_id)

    if status not in [LOGIN_SUCCESS, LOGIN_FAILURE]:
        get_logger().error("Unkown login status: {status}".format(status=status))
    elif (status == LOGIN_SUCCESS) and login_policy.login_success_enabled:
        event = LoginEvent().success(
            user_id=user_id,
            user_agent=user_agent,
            referrer=referrer,
            remote_addr=remote_address,
            header_keys=header_keys,
            document_uri=document_uri,
            session_id=session_id)
        TCellAgent.send(event)
    elif (status == LOGIN_FAILURE) and login_policy.login_failed_enabled:
        event = LoginEvent().failure(
            user_id=user_id,
            user_agent=user_agent,
            referrer=referrer,
            remote_addr=remote_address,
            header_keys=header_keys,
            document_uri=document_uri,
            session_id=session_id)
        TCellAgent.send(event)


def _instrument():
    import tcell_hooks.v1

    old_send_login_event = getattr(tcell_hooks.v1, "send_login_event")

    @wraps(old_send_login_event)
    def login_send(status,
                   session_id,
                   user_agent,
                   referrer,
                   remote_address,
                   header_keys,
                   user_id,
                   document_uri,
                   user_valid=None):
        safe_wrap_function(
            "Sending Login Event",
            report_login_event,
            {},
            status,
            user_id,
            session_id,
            document_uri,
            user_agent=user_agent,
            referrer=referrer,
            remote_address=remote_address,
            header_keys=header_keys)

        return old_send_login_event(status, session_id, user_agent, referrer, remote_address, header_keys, user_id,
                                    document_uri, user_valid)
    setattr(tcell_hooks.v1, "send_login_event", login_send)

    old_send_django_login_event = getattr(tcell_hooks.v1, "send_django_login_event")

    @wraps(old_send_django_login_event)
    def django_send(status, django_request, user_id, session_id, user_valid=None):
        safe_wrap_function(
            "Sending Django Login Event",
            report_login_event,
            django_request.META,
            status,
            user_id,
            session_id,
            django_request.get_full_path())
        return old_send_django_login_event(status, django_request, user_id, session_id, user_valid)
    setattr(tcell_hooks.v1, "send_django_login_event", django_send)

    old_send_flask_login_event = getattr(tcell_hooks.v1, "send_flask_login_event")

    @wraps(old_send_flask_login_event)
    def flask_send(status, flask_request, user_id, session_id, user_valid=None):
        safe_wrap_function(
            "Sending Flask Login Event",
            report_login_event,
            flask_request.environ,
            status,
            user_id,
            session_id,
            flask_request.url)
        return old_send_flask_login_event(status, flask_request, user_id, session_id, user_valid)
    setattr(tcell_hooks.v1, "send_flask_login_event", flask_send)


try:
    import tcell_hooks  # noqa

    if TCellAgent.get_agent():
        _instrument()
except ImportError as ie:
    pass
except Exception as e:
    LOGGER.debug("Could not instrument tcell_hooks: {e}".format(e=e))
    LOGGER.debug(e, exc_info=True)
