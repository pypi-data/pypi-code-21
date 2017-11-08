# -*- coding: utf-8 -*-

import logging


class ContextualFilter(logging.Filter):
    def __init__(self, instance, user=None, token=None):
        """Makes instance, user and token available to the logging formatter
        :param instance: ServiceNow instance name
        :param user: ServiceNow user
        :param token: ServiceNow OAuth refresh token
        """

        self._user = user
        self._token = token
        self._instance = instance

        super(ContextualFilter, self).__init__()

    def filter(self, log_record):
        log_record.user = self._user
        log_record.token = self._token
        log_record.instance = self._instance

        return True

