import requests

MAX_FILTER_SIZE = 1e7


def error_callback_pass():
    pass


def error_callback_raise():
    raise requests.HTTPError("Bad return code")


def queue_timeout_wait():
    print("here"*80)


ERROR_CALLBACKS = {
    "skip": error_callback_pass,
    "raise": error_callback_raise,

}

QUEUE_TIMEOUT_CALLBACKS = {
    "wait": queue_timeout_wait
}
