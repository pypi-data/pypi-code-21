__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection, \
   BaseDualRpConnection
from unicon.plugins.iosxr.settings import IOSXRSettings
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine, \
   IOSXRDualRpStateMachine
from unicon.plugins.generic import ServiceList, HAServiceList
from unicon.plugins.iosxr import service_implementation as svc
from unicon.plugins.iosxr.connection_provider import \
    IOSXRSingleRpConnectionProvider, IOSXRDualRpConnectionProvider

class IOSXRServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.configure = svc.Configure
        self.admin_execute = svc.AdminExecute
        self.admin_configure = svc.AdminConfigure

class IOSXRHAServiceList(HAServiceList):
    """ Generic dual rp services. """
    def __init__(self):
        super().__init__()
        self.execute = svc.HAExecute
#        self.switchover = svc.SwitchOver @@@ When HA supported


class IOSXRSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
    connection_provider_class = IOSXRSingleRpConnectionProvider 
    subcommand_list = IOSXRServiceList
    settings = IOSXRSettings()

class IOSXRDualRpConnection(BaseDualRpConnection):
    os = 'iosxr'
    series = None
    chassis_type = 'dual_rp'
    state_machine_class = IOSXRDualRpStateMachine
    connection_provider_class = IOSXRDualRpConnectionProvider
    subcommand_list = IOSXRHAServiceList
    settings = IOSXRSettings()
