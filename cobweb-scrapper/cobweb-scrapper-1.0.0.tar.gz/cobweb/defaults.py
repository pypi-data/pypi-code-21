import os

import requests
import time

USER_AGENT_PATH = os.path.join(
    *os.path.split(__file__)[:-1],
    "bbs",
    "user_agents.txt"
)

BLOCKED_WAIT_TIMEOUT = 2

FIRST_LEVEL_BORDER = .05
SECOND_LEVEL_BORDER = .15
THIRD_LEVEL_BORDER = .3

ITERATION_SIZE = 300

MAX_FILTER_SIZE = 1e7


def error_callback_pass():
    pass


def error_callback_raise():
    raise requests.HTTPError("Bad return code")


def queue_timeout_wait():
    time.sleep(BLOCKED_WAIT_TIMEOUT)


def queue_timeout_quit():
    from cobweb import Cobweb
    Cobweb().stop()


ERROR_CALLBACKS = {
    "skip": error_callback_pass,
    "raise": error_callback_raise,

}

QUEUE_TIMEOUT_CALLBACKS = {
    "wait": queue_timeout_wait,
    "quit": queue_timeout_quit
}
