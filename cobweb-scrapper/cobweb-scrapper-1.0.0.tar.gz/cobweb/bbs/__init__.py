import functools
import time
from random import choice

from cobweb.defaults import (
    BLOCKED_WAIT_TIMEOUT,
    USER_AGENT_PATH,
    FIRST_LEVEL_BORDER,
    SECOND_LEVEL_BORDER,
    ITERATION_SIZE,
    THIRD_LEVEL_BORDER
)


class BlockBypassSystem:

    ZERO = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3

    def __init__(self, user_agents_filename=USER_AGENT_PATH):
        self._accepted_requests = 0
        self._blocked_request = 0
        self._total_requests = 0
        self._iteration = ITERATION_SIZE
        self._blocked_wait_timeout = BLOCKED_WAIT_TIMEOUT
        self._is_active = True

        self.request_method_order = [
            [],
            ["modify_user_agent"],
            ["wait_timeout"],
            []
        ]

        self.response_method_order = [
            ["count_statistics"],
            ["remove_honeypot_links"],
            [],
            []
        ]
        self._honeypot_content_types = {"text/html", }

        with open(user_agents_filename) as file:
            self.headers_list = file.readlines()

    @property
    def block_level(self):
        blocked_percent = self._accepted_requests / self._total_requests
        if blocked_percent < FIRST_LEVEL_BORDER:
            return self.ZERO
        elif blocked_percent < SECOND_LEVEL_BORDER:
            return self.FIRST
        elif blocked_percent < THIRD_LEVEL_BORDER:
            return self.SECOND
        else:
            return self.THIRD

    @property
    def accepted_requests(self):
        return self._accepted_requests

    @accepted_requests.setter
    def accepted_requests(self, value):
        self._total_requests += value - self._accepted_requests
        self._accepted_requests = value
        self.check_iteration()

    @property
    def blocked_request(self):
        return self._blocked_request

    @blocked_request.setter
    def blocked_request(self, value):
        self._total_requests += value - self._blocked_request
        self._blocked_request = value
        self.check_iteration()

    def stop(self):
        self._is_active = False

    def start(self):
        self._is_active = True

    def check_iteration(self):
        if self._total_requests % self._iteration == 0:
            self._total_requests = 0
            self._blocked_request = 0
            self._accepted_requests = 0

    def monitor_responses(self, method):
        @functools.wraps(method)
        def inner(*args, **kwargs):
            response = method(*args, **kwargs)
            if self._is_active:
                return self.check_response(response)
            else:
                return response
        return inner

    def monitor_requests(self, method):
        @functools.wraps(method)
        def inner(*args, **kwargs):
            request = method(*args, **kwargs)
            if self._is_active:
                return self.take_action(request)
            else:
                return request
        return inner

    def count_statistics(self, response):
        if response.ok:
            self.accepted_requests += 1
        else:
            self.blocked_request += 1
        return response

    def check_response(self, response):
        for actions in reversed(self.response_method_order):
            for action in actions:
                response = getattr(self, action)(response)
        return response

    def remove_honeypot_links(self, response):
        if response.headers["content-type"] in self._honeypot_content_types:
            for link in response.data.select("a[style~='visibility:hidden']"):
                link.decompose()
            for link in response.data.select("a[style~='display:none']"):
                link.decompose()
        return response

    def take_action(self, request):
        for actions in reversed(self.request_method_order):
            for action in actions:
                request = getattr(self, action)(request)
        return request

    def modify_user_agent(self, request):
        user_agent = choice(self.headers_list)
        request.headers["user-agent"] = user_agent.strip()
        return request

    def wait_timeout(self, request):
        time.sleep(self._blocked_wait_timeout)
        return request
