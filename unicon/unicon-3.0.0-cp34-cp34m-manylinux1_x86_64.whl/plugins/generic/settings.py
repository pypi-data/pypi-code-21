"""
Module:
    unicon.plugins.generic

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
  This module defines the Generic settings to setup
  the unicon environment required for generic based
  unicon connection
"""
from unicon.settings import Settings


class GenericSettings(Settings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 0',
            'show version'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console 0',
            'exec-timeout 0'
        ]

        self.HA_STANDBY_UNLOCK_COMMANDS = [
            'redundancy',
            'main-cpu',
            'standby console enable'
        ]
        self.SWITCHOVER_COUNTER = 50
        self.SWITCHOVER_TIMEOUT = 500
        self.HA_RELOAD_TIMEOUT = 500
        self.RELOAD_TIMEOUT = 300

        # When connecting to a device via telnet, how long (in seconds)
        # to pause before checking the spawn buffer.
        self.ESCAPE_CHAR_CALLBACK_PAUSE_SEC = 0.25

        # sendline is called if the spawn buffer is empty after a pause, or
        # after trying a pause/spawn buffer check this many times.
        self.ESCAPE_CHAR_CALLBACK_PAUSE_CHECK_RETRIES = 12

        # Wait this amount of time (in seconds) after connecting to a device
        # via telnet before pressing <Enter>.
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 0.01

        # Sometimes a copy operation can fail due to network issues,
        # so copy at most this many times.
        self.MAX_COPY_ATTEMPTS = 2

        # If configuration mode cannot be entered on a newly reloaded device
        # because HA sync is in progress, wait this many times and for this long
        self.CONFIG_POST_RELOAD_MAX_RETRIES = 20
        self.CONFIG_POST_RELOAD_RETRY_DELAY_SEC = 9


#TODO
#take addtional dialogs for all service
#move all commands to settings
#
