"""
Module:
    unicon.plugins.linux

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
  This module defines the Linux settings to setup
  the unicon environment required for linux based
  unicon connection
"""
from unicon.settings import Settings


class LinuxSettings(Settings):
    """" Linux platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.LINUX_INIT_EXEC_COMMANDS = [
            'stty cols 200',
            'stty rows 200'
        ]

        ## Prompt recovery commands for Linux
        # Default commands: Enter key , Ctrl-C, Enter Key
        self.PROMPT_RECOVERY_COMMANDS = ['\r', '\x03', '\r']

