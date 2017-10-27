import logging

from tcell_agent.agent import TCellAgent, PolicyTypes

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def check_database_errors(request, exc_type, stack_trace):
    try:
        appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
        if appsensor_policy:
            from sqlalchemy.exc import DatabaseError
            if issubclass(exc_type, DatabaseError):
                appsensor_policy.sql_exception_detected(request._appsensor_meta, exc_type.__name__, stack_trace)
    except ImportError:
        pass
    except Exception as exception:
        LOGGER.debug("Exception during database errors check: {e}".format(e=exception))
        LOGGER.debug(exception, exc_info=True)
