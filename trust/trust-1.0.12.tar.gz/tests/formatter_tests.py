from abc import ABCMeta, abstractmethod
import trust
from .logged_tests import LoggedTests


class FormatterTests(LoggedTests, metaclass=ABCMeta):
    @abstractmethod
    def _get_formatter(self, finder):
        pass

    def _process_default(self, value):
        formatter = self._get_formatter(FinderStubWithValue(value))
        return formatter.process("/", trust.Credentials.get_empty())


class FinderStubWithValue():
    def __init__(self, value):
        self._value = value

    def access_as(self, credentials):
        pass

    def find(self, query, optional):
        return self._value
