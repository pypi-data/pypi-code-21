__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic.statements import GenericStatements, password_handler
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.helpers import sendline


patterns = IOSXRPatterns()

class IOSXRStatements(GenericStatements):

    def __init__(self):
        super().__init__()
        self.password_stmt = Statement(pattern=patterns.password_prompt,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.commit_replace_stmt = Statement(pattern=patterns.commit_replace_prompt,
                                     action=sendline,
                                     args={'command': 'yes'},
                                     loop_continue=True,
                                     continue_timer=False)


