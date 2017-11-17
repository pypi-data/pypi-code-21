#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
pcrunner.windows_service
------------------------

Entry poing for Passive Check Runner as Windows Service
'''

import win32service
import win32serviceutil
import win32event


class PassiveCheckRunnerService(win32serviceutil.ServiceFramework):
    '''
    Passive Check Runner as Windows Service
    '''

    # you can NET START/STOP the service by the following name
    _svc_name_ = 'pcrunner'
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = 'Passive Check Runner'
    # this text shows up as the description in the SCM
    _svc_description_ = 'Runs passive checks and post them to NSCAweb.'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    # core logic of the service
    def SvcDoRun(self):
        import sys
        from distutils.sysconfig import get_python_lib

        site_packages_dir = get_python_lib()
        # HACK: it can't seem find its site packages
        # put it in hard on sys.path
        # TODO: check what's happening
        sys.path.insert(0, site_packages_dir)

        from pcrunner.main import setup_logging
        from pcrunner.main import setup_syslog_with_config_opts
        from pcrunner.main import PassiveCheckRunner

        # Setup basic logging
        setup_logging()

        # Get configurtation
        import configuration

        config = configuration.Config()

        # Get logging args
        log_args = config.subset('log_file', 'verbose', 'syslog_server',
                                 'syslog_port')
        # Logging with config opts
        setup_syslog_with_config_opts(**log_args)

        # Get PassiveCheckRunner args
        pcrunner_args = config.subset('nsca_web_url', 'nsca_web_username',
                                      'nsca_web_password', 'hostname',
                                      'command_file', 'result_file',
                                      'result_dir', 'max_procs', 'interval',
                                      'lines_per_post', 'pid_file',
                                      'http_timeout', 'max_line_size')

        # Init Passive Check Runner
        pcrunner = PassiveCheckRunner(**pcrunner_args)

        rc = None

        # If the stop event hasn't been fired keep looping
        while rc != win32event.WAIT_OBJECT_0:
            pcrunner.start()
            # Block for x seconds and listen for a stop event
            rc = win32event.WaitForSingleObject(
                self.hWaitStop,
                pcrunner.interval * 1000,
            )

    # Called when we're being shut down
    def SvcStop(self):
        # Tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # Fire the stop event
        win32event.SetEvent(self.hWaitStop)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PassiveCheckRunnerService)
