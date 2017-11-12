#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from cloudshell.devices.snmp_handler_interface import SnmpHandlerInterface


class BaseSnmpFlow(object):
    def __init__(self, snmp_handler, logger):
        """
        :param snmp_handler:
        :type snmp_handler: SnmpHandlerInterface
        :param logger:
        :return:
        """
        self._snmp_handler = snmp_handler
        self._logger = logger


class AutoloadFlow(BaseSnmpFlow):
    @abstractmethod
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        pass
