import logging

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import django_meta
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.instrumentation.djangoinst.utils import django15or16

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def instrument_database_error_wrapper():
    if not django15or16:
        try:
            from django.db.utils import DatabaseErrorWrapper

            def _tcell_exit(_tcell_original_exit, self, exc_type, exc_value, traceback):
                if exc_type is not None:
                    programming_error = getattr(self.wrapper.Database, "ProgrammingError")
                    operational_error = getattr(self.wrapper.Database, "OperationalError")
                    if issubclass(exc_type, programming_error) or issubclass(exc_type, operational_error):
                        appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
                        if appsensor_policy is not None:
                            request = GlobalRequestMiddleware.get_current_request()
                            if request is not None:
                                meta = django_meta(request)
                                appsensor_policy.sql_exception_detected(meta, exc_type.__name__, traceback)

                return _tcell_original_exit(self, exc_type, exc_value, traceback)

            InstrumentationManager.instrument(DatabaseErrorWrapper, "__exit__", _tcell_exit)
        except Exception as e:
            LOGGER.debug("Could not instrument database error wrapper")
            LOGGER.debug(e, exc_info=True)


def handle_django15_exception(request, exc_type, _, traceback):
    if django15or16:
        try:
            appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
            if appsensor_policy:

                from django.db.utils import DatabaseError

                if exc_type is not None and issubclass(exc_type, DatabaseError):
                    meta = django_meta(request)
                    appsensor_policy.sql_exception_detected(meta, exc_type.__name__, traceback)

        except ImportError:
            pass
        except Exception as exception:
            LOGGER.debug("Exception in handle_django15_exception: {e}".format(e=exception))
            LOGGER.debug(exception, exc_info=True)
