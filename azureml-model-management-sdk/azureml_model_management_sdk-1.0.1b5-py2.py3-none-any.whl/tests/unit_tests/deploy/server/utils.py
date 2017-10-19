# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import random
from azureml.common import Configuration


def id_gen(bits=32):
    """ Returns a n-bit randomly generated int """
    return int(random.getrandbits(bits))


def services_resource(name=None, version=None):
    resource = '/services'

    if name is not None:
        resource += '/' + name

    if version is not None:
        resource += '/' + version

    return Configuration().host + resource
