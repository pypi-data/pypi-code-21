# coding: utf-8
# Copyright (c) 2016, 2017, Oracle and/or its affiliates. All rights reserved.

from . import audit, config, constants, core, decorators, database, exceptions, identity, load_balancer, object_storage, regions
from .base_client import BaseClient
from .request import Request
from .response import Response
from .signer import Signer
from .version import __version__  # noqa
from .waiter import wait_until


__all__ = [
    "BaseClient", "Error", "Request", "Response", "Signer",
    "audit", "config", "constants", "core", "decorators", "database", "exceptions",
    "identity", "load_balancer", "object_storage", "regions",
    "wait_until"
]

import warnings
warnings.warn("The oraclebmc package is deprecated and will no longer be maintained starting March 2018. Please upgrade to the oci package to avoid interruption at that time. More info is available at https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/backward-compatibility.html", DeprecationWarning, stacklevel=2)
