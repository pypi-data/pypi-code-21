import sys
import unittest

from types import ModuleType
from mock import Mock, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.flaskinst.database import check_database_errors


class DatabaseError(object):
    pass


class OperationalError(DatabaseError):
    pass


class SomeOtherError(object):
    pass


sqlalchemy = ModuleType("sqlalchemy")
exc = ModuleType("exc")


class DatabaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sqlalchemy.__file__ = sqlalchemy.__name__ + ".py"
        sqlalchemy.__path__ = []
        sys.modules[sqlalchemy.__name__] = sqlalchemy

        exc.__file__ = exc.__name__ + ".py"
        sys.modules["sqlalchemy.exc"] = exc

        setattr(exc, "DatabaseError", DatabaseError)
        setattr(exc, "OperationalError", OperationalError)

    def appsensor_policy_empty_check_database_errors_test(self):
        request = Mock()
        tb = Mock()

        with patch.object(TCellAgent, "get_policy", return_value=None) as patched_get_policy:
            check_database_errors(request, OperationalError, tb)

            self.assertTrue(patched_get_policy.called)

    def appsensor_policy_with_someothererror_check_database_errors_test(self):
        appsensor_policy = Mock()
        request = Mock()
        tb = Mock()

        with patch.object(TCellAgent, "get_policy", return_value=appsensor_policy) as patched_get_policy:
            check_database_errors(request, SomeOtherError, tb)

            self.assertTrue(patched_get_policy.called)

            self.assertFalse(appsensor_policy.sql_exception_detected.called)

    def appsensor_policy_with_operationerror_check_database_errors_test(self):
        appsensor_policy = Mock()
        request = Mock()
        request._appsensor_meta = AppSensorMeta()
        tb = Mock()

        with patch.object(TCellAgent, "get_policy", return_value=appsensor_policy) as patched_get_policy:
            check_database_errors(request, OperationalError, tb)

            self.assertTrue(patched_get_policy.called)

            appsensor_policy.sql_exception_detected.assert_called_once_with(request._appsensor_meta, "OperationalError", tb)
