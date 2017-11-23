##############################################################################
# Copyright (c) 2017 ZTE Corp and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from qtip.base.constant import BaseProp
from qtip.collector.parser.grep import GrepParser


class CollectorProp(BaseProp):
    TYPE = 'type'
    PARSERS = 'parsers'
    PATHS = 'paths'


def load_parser(type_name):
    if type_name == GrepParser.TYPE:
        return GrepParser
    else:
        raise Exception("Invalid parser type: {}".format(type_name))
