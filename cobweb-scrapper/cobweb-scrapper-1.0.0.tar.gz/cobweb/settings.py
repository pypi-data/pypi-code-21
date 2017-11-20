import json
import logging
import os
from types import FunctionType

import yaml

from cobweb.defaults import ERROR_CALLBACKS, QUEUE_TIMEOUT_CALLBACKS


class Settings:

    ERROR_SKIP = "skip"

    QUEUE_WAIT = "wait"

    whitelist = {
        "use_bbs",
        "keep_alive_timeout",
        "page_load_timeout",
        "_success_codes",
        "_failure_codes",
        "on_failure_action",
        "on_failure_callback",
        "on_queue_timeout_action",
        "on_queue_timeout_callback",
    }

    __slots__ = whitelist

    def __init__(
            self,
            use_bbs=True,
            keep_alive_timeout=5,
            page_load_timeout=3,
            success_codes=frozenset({200, 202}),
            failure_codes=frozenset({400, 402, 403, 500, 502}),
            on_failure_action=ERROR_SKIP,
            on_queue_timeout_action=QUEUE_WAIT,
            on_failure_callback: FunctionType = None,
            on_queue_timeout_callback: FunctionType = None,
    ):

        self.use_bbs = use_bbs
        self.keep_alive_timeout = keep_alive_timeout
        self.page_load_timeout = page_load_timeout
        self._success_codes = set(success_codes)
        self._failure_codes = set(failure_codes)
        self.on_failure_action = on_failure_action
        self.on_failure_callback = on_failure_callback
        self.on_queue_timeout_action = on_queue_timeout_action
        self.on_queue_timeout_callback = on_queue_timeout_callback

    @property
    def logger(self):
        return logging.getLogger("cobweb.settings")

    @property
    def success_codes(self):
        return self._success_codes

    @success_codes.setter
    def success_codes(self, value):
        self._success_codes = set(value)

    @property
    def failure_codes(self):
        return self._failure_codes

    @failure_codes.setter
    def failure_codes(self, value):
        self._failure_codes = set(value)

    @property
    def attributes(self):
        return {attr: getattr(self, attr) for attr in self.whitelist}

    def default_error_handler(self):
        if self.on_failure_callback:
            return self.on_failure_callback
        else:
            return ERROR_CALLBACKS[self.on_failure_action]

    def default_queue_timeout_handler(self):
        if self.on_queue_timeout_callback:
            return self.on_queue_timeout_callback
        else:
            return QUEUE_TIMEOUT_CALLBACKS[self.on_queue_timeout_action]

    def update(self, data: dict) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    def to_json(self, filename: str) -> None:
        with open(Settings.get_absolute_path(filename), "w") as file:
            json.dump(self.attributes, file)

    def to_yaml(self, filename: str) -> None:
        with open(Settings.get_absolute_path(filename), "w") as file:
            yaml.dump(self.attributes, file, default_flow_style=False)

    @classmethod
    def from_json(cls, filename: str) -> 'Settings':
        settings = Settings()
        with open(Settings.get_absolute_path(filename)) as file:
            settings_data = Settings.sanitize(json.load(file), cls.whitelist)
            settings.update(settings_data)
        return settings

    @classmethod
    def from_yaml(cls, filename: str) -> 'Settings':
        settings = Settings()
        with open(Settings.get_absolute_path(filename)) as file:
            settings_data = Settings.sanitize(yaml.load(file), cls.whitelist)
            settings.update(settings_data)
        return settings

    @staticmethod
    def sanitize(data: dict, whitelist: set) -> dict:
        return {key: value for key, value in data.items() if key in whitelist}

    @staticmethod
    def get_absolute_path(relative_path: str) -> str:
        return os.path.abspath(
            os.path.expandvars(
                os.path.expanduser(
                    relative_path
                )
            )
        )
