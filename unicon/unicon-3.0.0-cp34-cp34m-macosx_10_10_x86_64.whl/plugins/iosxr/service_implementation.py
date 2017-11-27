__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic import service_implementation as svc
from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog

class Configure(svc.Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.service_name = 'config'

class AdminExecute(svc.Execute):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'run'
        self.end_state = 'enable'
        self.service_name = 'run'


class AdminConfigure(svc.Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'admin'
        self.end_state = 'enable'
        self.service_name = 'admin'

class HAExecute(svc.HaExecService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'execute'

    def call_service(self, command,
                     reply=Dialog([]),
                     target='active',
                     timeout=None,
                     *args,
                     **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        if target is 'active':
            handle = con.active
        elif target is 'standby':
            handle = con.standby
        elif target is 'a':
            handle = con.a
        elif target is 'b':
            handle = con.b
        handle.state_machine.go_to(self.start_state,
                                   handle.spawn,
                                   context=con.context,
                                   timeout=con.connection_timeout,
                                   )
        # @@@ Note: below has been added by iormisto
        dialog = self.service_dialog(handle, service_dialog=reply)
        con.sendline(command)
        try:
            self.result = dialog.process(handle.spawn,
                                         timeout=timeout,
                                         context=self.context)
        except Exception as err:
            raise SubCommandFailure("Command execution failed", err)