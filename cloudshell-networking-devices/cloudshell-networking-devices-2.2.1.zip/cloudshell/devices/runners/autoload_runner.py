#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractproperty, ABCMeta

from cloudshell.devices.runners.interfaces.autoload_runner_interface import AutoloadOperationsInterface


class AutoloadRunner(AutoloadOperationsInterface):
    __metaclass__ = ABCMeta

    def __init__(self, resource_config):
        """
        Facilitate SNMP autoload,
        :param supported_os:
        :param context:
        :param Cli cli:
        :param QualiSnmp snmp_handler:
        """

        self.resource_config = resource_config

    @abstractproperty
    def autoload_flow(self):
        """ Autoload flow property
        :return: AutoloadFlow object
        """

        pass

    def discover(self):
        """Enable and Disable SNMP communityon the device, Read it's structure and attributes: chassis, modules,
        submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """
        return self.autoload_flow.execute_flow(self.resource_config.supported_os,
                                               self.resource_config.shell_name,
                                               self.resource_config.family,
                                               self.resource_config.name)
