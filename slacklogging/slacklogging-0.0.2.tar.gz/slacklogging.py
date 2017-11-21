"""Handler of logging for Slack.

If you don't want to log everything on slack, we recommend to have different logger. logger is kind
of Singleton, so once you set up logger with got by logging.getLogger('slack'), you can access the
logger from anywhere by logging.getLogger('slack').

logger = logging.getLogger(__name__)  # For general
slack_logger = logging.getLogger('slack')  # For slack.
slack_logger.addHandler(slacklogging.Handler())
"""
import logging
import threading
import time
from typing import (
    Callable,
    List,
)

import requests
import requests.exceptions


__version__ = "0.0.2"
__author__ = "Motoki Naruse"
__email__ = "motoki@naru.se"
__all__ = ['TimebasedCondition', 'Handler']


class TimebasedCondition:
    """When same log message is came in given seconds, don't send it to Slack.

    This condition class checks message before format it, so the message might has "%s". So
    logger.error("Hello %s", "World") and logger.error("Hello %s", "Python") is same message for
    this class.
    """
    def __init__(self, seconds: int) -> None:
        self._seconds = seconds
        self._state = {}

    def __call__(self, record: logging.LogRecord) -> bool:
        now = time.time()
        if self._seconds < (now - self._state.get(record.msg, 0)):
            self._state[record.msg] = now
            return True
        return False


class Handler(logging.Handler):
    def __init__(
            self,
            *,
            token: str,
            channel: str,
            timeout: float=10,
            conditions: List[Callable[[logging.LogRecord], bool]]=[],
            **kwargs
    ) -> None:
        """
        :param token: Slack API token.
        :param channel: Channel of Slack. This handler will post message on this channel.
        :param timeout: Timeout for API request of Slack.
        :param condifitons: Each element is Callable, take logging.Record as the first argument and
        return True when need to send message to Slack. When all condifitons didn't return False,
        this handler sends message to Slack.
        """
        super().__init__(**kwargs)
        self.token = token
        self.channel = channel
        self.timeout = timeout
        self.conditions = conditions

    def post(self, record: logging.LogRecord) -> None:
        try:
            response = requests.post(
                "https://slack.com/api/files.upload",
                data={
                    'token': self.token,
                    'channels': [self.channel],
                    'content': self.format(record)
                },
                timeout=self.timeout
            )
            print(response.text)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            self.handleError(record)

    def emit(self, record: logging.LogRecord) -> None:
        if not all(condition(record) for condition in self.conditions):
            return

        threading.Thread(target=self.post, args=(record, )).start()
