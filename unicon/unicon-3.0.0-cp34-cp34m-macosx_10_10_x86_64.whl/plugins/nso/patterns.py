""" NSO regex patterns """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.patterns import UniconCorePatterns

class NsoPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        # Prompt pattern syntax is different from the generic plugin
        # The regex group match is grouped around the prompt itself
        # To truncate the prompt from command output, truncate_trailing_prompt is used from nso.utils
        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no\)'
        self.cisco_prompt = r'^.*(\w+@\w+#)\s*$'
        self.juniper_prompt = r'^.*(\w+@\w+>)\s*$'
        self.cisco_or_juniper_prompt = r'^.*(\w+@\w+[#>])\s*$'
        self.cisco_config_prompt = r'^.*(\w+@\w+\(config.*\)#)\s*$'
        self.juniper_config_prompt = r'^.*(\w+@\w+%)\s*$'
        self.cisco_or_juniper_config_prompt = r'^.*(\w+@\w+(\(config.*\)#|%))\s*$'
        self.cisco_commit_changes_prompt = r'Uncommitted changes found, commit them\? \[yes/no/CANCEL\]'
        self.juniper_commit_changes_prompt = r'Discard changes and continue\? \[yes,no\]'
