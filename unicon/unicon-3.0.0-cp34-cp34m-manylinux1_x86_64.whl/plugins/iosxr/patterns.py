__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"


from unicon.plugins.generic.patterns import GenericPatterns

# This module contains all the patterns required in the IOSXR implementation.

class IOSXRPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^.*?(%N|ios)\s?#'
        self.config_prompt = r'^.*?(%N|ios)\(config.*\)\s?#\s?'
        self.telnet_prompt = r'^.*Escape character is.*$'
        self.username_prompt = r'^.*([Uu]sername|[Ll]ogin):\s*$'
        self.password_prompt = r'^.*([Pp]assword|Enter secret(\sagain)?): ?$'
        self.commit_changes_prompt = r'Uncommitted changes found, commit them before exiting'
        self.logout_prompt = r'^.*Press RETURN to get started\..*$'
        self.commit_replace_prompt = r'Do you wish to proceed?'
        self.xr_admin_prompt = r'^.*sysadmin-vm:0_(.*)\s?#\s?$'
        self.xr_run_prompt = r'^.*\[xr-vm_.*:~\]\s?\$\s?$'
        self.unreachable_prompt = r'apples are green but oranges are red'
        self.configuration_failed_message = r'^.*Please issue \'show configuration failed \[inheritance\].*$'
        self.standby_prompt = r'^.*This \(D\)RP Node is not ready or active for login \/configuration.*$'
        self.rp_extract_status = r'^\d+\s+(\w+)\s+\-?\d+.*$'
