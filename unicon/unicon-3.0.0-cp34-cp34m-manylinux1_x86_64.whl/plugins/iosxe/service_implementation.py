""" Generic IOS-XE service implementations. """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Myles Dear <pyats-support@cisco.com>"


from unicon.eal.dialogs import Dialog

from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute,\
    HaConfigureService as GenericHAConfigure,\
    HaExecService as GenericHAExecute,\
    HAReloadService as GenericHAReload,\
    SwitchoverService as GenericHASwitchover


from .service_statements import overwrite_previous, are_you_sure, \
    delete_filename, confirm, wish_continue, want_continue


# Simplex Services
# ----------------
class Configure(GenericConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply + Dialog([are_you_sure]),
                             timeout=timeout, *args, **kwargs)


class Config(Configure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        self.connection.log.warn('**** This service is deprecated. ' +
                                 'Please use "configure" service ****')
        super().call_service(command, reply=reply + Dialog([are_you_sure,
                                                            wish_continue]),
                             timeout=timeout, *args, **kwargs)


class Execute(GenericExecute):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command,
                             reply=reply + Dialog([overwrite_previous,
                                                   delete_filename,
                                                   confirm,
                                                   want_continue]),
                             timeout=timeout, *args, **kwargs)

# HA Services
# -----------
class HAConfigure(GenericHAConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply + Dialog([are_you_sure]),
                             timeout=timeout, *args, **kwargs)


class HAConfig(HAConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        self.connection.log.warn('**** This service is deprecated. ' +
                                 'Please use "configure" service ****')
        super().call_service(command, reply=reply + Dialog([are_you_sure,
                                                            wish_continue]),
                             timeout=timeout, *args, **kwargs)


class HAExecute(GenericHAExecute):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command,
                             reply=reply + Dialog([overwrite_previous,
                                                   delete_filename,
                                                   confirm,
                                                   want_continue]),
                             timeout=timeout, *args, **kwargs)


class HAReload(GenericHAReload):
        # Non-stacked platforms such as ASR and ISR do not use the same
        # reload command as the generic implementation (whose reload command
        # covers stackable platforms only).
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command or "reload",
                             timeout=timeout, *args, **kwargs)


class HASwitchover(GenericHASwitchover):
    def call_service(self, command=[], dialog=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command,
                             dialog = dialog + Dialog([confirm, ]),
                             timeout=timeout, *args, **kwargs)
