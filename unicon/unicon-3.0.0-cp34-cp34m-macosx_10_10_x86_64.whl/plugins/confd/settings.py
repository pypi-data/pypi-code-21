""" Defines the settings for ConfD based unicon connections """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.settings import Settings


class ConfdSettings(Settings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.CISCO_INIT_COMMANDS = [
            'screen-length 0',
            'screen-width 0',
            'idle-timeout 0'
        ]

        self.JUNIPER_INIT_COMMANDS = [
            'set screen length 0',
            'set screen width 0',
            'set idle-timeout 0'
        ]

        # Prompt prefixes will be removed from the output by the configure() and execute() services
        self.JUNIPER_PROMPT_PREFIX = "\[edit\]"

        self.ERROR_PATTERN = [
            'Error:',
            'syntax error',
            'Aborted',
            'result false'
        ]