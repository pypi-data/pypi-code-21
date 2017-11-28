"""
ActionChain wait in Selenium.

credit to Kim Homann for the solution and
https://stackoverflow.com/questions/36572190/specify-wait-
time-between-actions-when-using-selenium-actionchains#
answer-41270655
"""

from selenium.webdriver import ActionChains
from time import sleep

__version__ = '1.0.0'


class Actions(ActionChains):
    """Add a sleep command to an action chain."""

    def wait(self, seconds: float):
        """Sleep for a specified number of seconds within an ActionChain."""
        self._actions.append(lambda: sleep(seconds))
        return self

if __name__ == '__main__':  # pragma: no cover
    initialization = Actions
