# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
azureml.deploy.deploy_client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a factory for creating Deployment Clients.
"""

from __future__ import absolute_import

from azureml.common import Configuration, HttpClient
from .operationalization import Operationalization

import logging
import imp
import os


log = logging.getLogger(__name__)


class DeployClient(object):
    """
    Factory for creating Deployment Clients.

    **Basic Usage:**

    >>> auth = ('username', 'password')
    >>> client = DeployClient('url', use='MLServer', auth=auth)

    **Module implementation plugin with `use` property:**

    Find and Load `module` as defined by `use` from namespace str:

    >>> client = DeployClient('url', use='azureml.deploy.server.MLServer')
    >>> client = DeployClient('url', use='MLServer')

    Find and Load `module` from a file/path tuple:

    >>> use = ('azureml.deploy.server.MLServer', '/path/to/mlserver.py')
    >>> client = DeployClient('url', use=use)

    Find and Load `module` from an import reference:

    >>> from azureml.deploy.server import MLServer
    >>> client = DeployClient('url', use=MLServer)
    """
    
    def __new__(cls, *args, **kwargs):
        use = kwargs.pop('use')
        mixin = module = None  # The candidate module
        
        def load_module(namespace, name):
            path = os.path.join(*namespace.split('.'))
            f, filename, desc = imp.find_module(name.lower(), [path])
            log.debug('%s.%s.%s', desc, filename, f)

            return imp.load_module(namespace + '.' + name, f, filename, desc)

        # Find and Load `module` as defined by `use`
        # ----------------------------------------------------------------------
        # 1. Load by module namespace`use='azureml.deploy.server.MLServer'`
        # 2. Load by source file `use=('module', '/path/to/module.py'))`        
        # 3. Load by module ref `from pkg import Module; use=Module`

        try:            
            log.debug('Loading module: %s', use)
            
            if type(use) is str: # Load module by str source
                # capture module name and namespace
                pkgs = use.split('.')
                namespace = {
                    'MLServer': 'azureml.deploy.server',
                    'Azure????': 'azureml.deploy.cloud'  # TODO - real name
                }.pop(use, '.'.join(pkgs[:-1]))

                module = load_module(namespace, pkgs[-1])
            elif isinstance(use, tuple):  # Load by module source
                module = imp.load_source(*use)
            elif issubclass(use, Operationalization):  # Load by module ref
                mixin = module = use
            else:
                raise TypeError('Inappropriate type supplied for `use`.')
        except Exception as e:
            msg = 'No module named `use={0}`\n   {1}: {2}'.\
                  format(str(use), type(e).__name__, str(e))
            log.error(msg)
            raise ImportError(msg)

        log.debug('Module loaded: %s', module)    

        # Compose `module` into `this` DeployClient:
        # ----------------------------------------------------------------------
        # 1. Assert it implements `Operationalization`
        # 2. Create by retrieving a user-defined function object from a class
        
        name = module.__name__

        for element in (getattr(module, name) for name in dir(module)):
            try:
                if (issubclass(element, Operationalization) and
                    element.__name__ != Operationalization.__name__):
                    mixin = element
            except Exception:
                continue

        if mixin is None:
            raise ImportError('No module named use={0}'.format(str(use)))
                
        name = '{}Composed{}'.format(cls.__name__, mixin.__name__)
        bases = (mixin, cls)
        return object.__new__(type(name, bases, dict(cls.__dict__)))        
    
    def __init__(self, host, auth=None, use=None):
        """
        Create a new Deployment Client.

        :param host: Host endpoint.
        :param auth: (optional) Authentication context. Not all deployment
               clients require authentication.
        :param use: Deployment implementation to use (ex. 'MLServer')
        """
        super(DeployClient, self).__init__()
        log.debug('DeployClient.__init__()')
        config = Configuration()
        config.host = host

        # Lifecycle init
        self.initializer(HttpClient(host=config.host), config)
        
        # Lifecycle authenticate (optional for different implementations)
        if auth is not None:
            self.authentication(auth)

    def __del__(self):
        """
        Lifecycle destroy
        """
        self.destructor()
