# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

from __future__ import absolute_import

# import into deploy package
from .deploy_client import DeployClient
from .operationalization import Operationalization, ServiceDefinition
from .server.mlserver_adapter import MLServerAdapter

