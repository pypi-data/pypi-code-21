__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.generic.patterns import GenericPatterns

class CimcPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.prompt = r'^(.*)\S+\s?(/\w+)*\s?#\s*$'
