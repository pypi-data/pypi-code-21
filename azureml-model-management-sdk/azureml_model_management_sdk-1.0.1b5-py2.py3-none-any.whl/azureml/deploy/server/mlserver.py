# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
azureml.deploy.server.mlserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a service implementation for the ML Server.
"""

import logging
from azureml.authentication import ADAuthentication, AADAuthentication
from ..operationalization import Operationalization
from .mlserver_adapter import MLServerAdapter
from .services import WebServiceService
from .service import Service
                    
log = logging.getLogger(__name__)


class MLServer(Operationalization):
    """
    This module provides a service implementation for the ML Server.
    """
        
    def initializer(self, http_client, config, adapters=None):
        """
        **Override**

        Init lifecycle method called by the framework, invoked during
        construction. Sets up attributes and invokes initializers for the class
        hierarchy.

        :param http_client: The http request session to manage and persist
               settings across requests (auth, proxies).
        :param config: The global configuration.
        :param adapters: A dict of transport adapters by url.
        """

        log.debug('MLServer.initializer(): \n %s', config.host)

        self._http_client = http_client
        self._service = WebServiceService(self._http_client)
        self._aad_options = None

        # -- Apply custom request adapters for MLServer --
        if adapters is None:
            adapters = [(config.host, MLServerAdapter())]

        # default prefix url to `host` if no mount prefix was given
        if not isinstance(adapters, list):
            adapters = [(config.host, adapters)]
                
        try:
            for adapter_set in adapters:                
                prefix = adapter_set[0]
                adapter = adapter_set[1]                
                self._http_client.mount(prefix, adapter)
        except Exception as e:
            msg = 'Invalid `adapter` {0}\n{1}'.format(type(e).__name__, str(e))
            raise ValueError(msg)            

    def destructor(self):
        """
        **Override**

        Destroy lifecycle method called by the framework. Invokes destructors
        for the class hierarchy.
        """
        log.debug('MLServer.destructor()')

        self._http_client = None
        self._service = None
        
    def authentication(self, context):
        """
        **Override**

        Authentication lifecycle method method called by the framework. Invokes
        the authentication entry-point for the class hierarchy.

        ML Server supports two forms of authentication contexts:

        * LDAP: tuple `(username, password)`
        * Azure Active Directory (AAD): dict `{...}`
        * access-token: str `=4534535`

        :param context: The authentication context: LDAP, Azure Active Directory
               (AAD), or exsisting `access-token` string.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """
        log.debug('MLServer.authentication()')
        client = self._http_client

        # -- Authentication --
        if isinstance(context, dict):
            access_token = AADAuthentication(context).acquire_token()
        elif isinstance(context, tuple):
            access_token = ADAuthentication(client).acquire_token(
                context[0], context[1])
        else:
            access_token = context

        client.authorization = access_token

    def get_service(self, name, **opts):
        """
        Get a web service for consumption.

        `Complete documentation <https://go.microsoft.com/fwlink/?linkid=
        836352>`_.

        >>> service = client.get_service('example', version='v1.0.1')
        >>> print(service)
        <ExampleService>
           ...
           ...
           ...

        :param name: The web service name.
        :param opts: The optional web service `version`. If `version=None` the
               most recent service will be returned.
        :returns: A new instance of :class:`~.service.Service`.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """
        log.debug('MLServer.get_service(): \n   %s', name)
    
        version = opts.pop('version', None)
                
        # List service by name and version        
        if (name and version) is not None:
            service = self._service.get_service(name, version)
        else:            
            service = self._service.get_latest_service(name)

        if service is None or len(service) == 0:
            raise ValueError("No service found for {} version {}".format(name, version))
        return Service(service, self._http_client)

    def list_services(self, name=None, **opts):
        """
        List the different published web services on the ML Server.

        `Complete documentation <https://go.microsoft.com/fwlink/?linkid=
        836352>`_.

        The service `name` and service `version` are optional. This call allows
        you to retrieve service information regarding:

        * All services published
        * All versioned services for a specific named service
        * A specific version for a named service

        Users can use this information along with the
        :py:meth:`~.MLServer.get_service` operation to interact with and consume
        the web service.

        **Example:**

        >>> all_services = client.list_services()
        >>> all_versions = client.list_services('add-service')
        >>> service = client.list_services('add-service', version='v1')

        :param name: The web service name.
        :param opts: The optional web service `version`.
        :returns: A `list` of service metadata.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """
        log.debug('MLServer.list_services(): \n   %s\n   %s', name, opts)

        version = opts.pop('version', None)

        # List service by name and version        
        if (name and version) is not None:
            services = self._service.get_service(name, version)
            services = services if isinstance(services, list) else [services]
        elif name is not None and version is None:
            # List service versions            
            services = self._service.get_service_versions(name)
        else:
            # List all services
            services = self._service.get_all_services()

        return services

    def delete_service(self, name, **opts):
        """
        Delete a web service.

        `Complete documentation <https://go.microsoft.com/fwlink/?linkid=
        836352>`_.

        >>> success = client.delete_service('example', version='v1.0.1')
        >>> print(success)
        True

        :param name: The web service name.
        :param opts: The web service `version` (`version='v1.0.1`).
        :returns: A `bool` indicating the service deletion was succeeded.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """

        log.debug('MLServer.delete_service(): \n   %s\n   %s', name, opts)

        # -- Delete Service, failures will raise exception --        
        version = opts.pop('version', None)
        if version is None:
            raise ValueError('Missing the required parameter `version`')

        self._service.delete_service(name, version)
        return True

    def deploy_service(self, name, **opts):
        """
        Publish an new web service on the ML Server by `name` and `version`.

        **Example:**

        >>> opts = {
              'version': 'v1.0.0',
              'description': 'Service description.',
              'code_fn': run,
              'init_fn': init,
              'objects': {'local_obj': 50},
              'models': {'model': 100},
              'inputs': {'x': int},
              'outputs': {'answer': float},
              'artifacts': ['histogram.png'],
              'alias': 'consume_service_fn_alias'
            }
        >>> service = client.deploy('regression', **opts)
        >>> res = service.consume_service_fn_alias(100)
        >>> answer = res.output('answer')
        >>> histogram = res.artifact('histogram.png')

        **NOTE:** Using `deploy_service()` in this fashion is identical to
        publishing a service using the fluent APIS
        :py:meth:`~azureml.deploy.operationalization.ServiceDefinition.deploy`.

        :param name: The unique web service name.
        :param opts: The service properties to publish. `opts` dict supports the
               following optional properties:

               * version (str) - Defines a unique alphanumeric web service
                 version. If the version is left blank, a unique `guid` is
                 generated in its place. Useful during service development
                 before the author is ready to officially publish a semantic
                 version to share.
               * description (str) - The service description.
               * code_str (str) - A block of python code to run and evaluate.
               * init_str (str) - A block of python code to initialize service.
               * code_fn (function) - A Function to run and evaluate.
               * init_fn (function) - A Function to initialize service.
               * objects (dict) - Name and value of `objects` to include.
               * models (dict) - Name and value of `models` to include.
               * inputs (dict) - Service input schema by `name` and `type`.
                  The following types are supported:
                     - int
                     - float
                     - str
                     - bool
                     - numpy.array
                     - numpy.matrix
                     - numpy.DataFrame
               * outputs (dict) - Defines the web service output schema. If
                  empty, the service will not return a response value.
                  `outputs` are defined as a dictionary `{'x'=int}` or
                  `{'x': 'int'} that describes the output parameter names and
                  their corresponding data `types`.
                 The following types are supported:
                     - int
                     - float
                     - str
                     - bool
                     - numpy.array
                     - numpy.matrix
                     - numpy.DataFrame
               * artifacts (list) - A collection of file artifacts to return.
                 File content is encoded as a `Base64 String`.
               * alias (str) - The consume function name. Defaults to `consume`.
                  If `code_fn` function is provided, then it will use that
                  function name by default.

        :returns: A new instance of :class:`~.service.Service` representing the
                  service `deployed`.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """

        log.debug('MLServer.deploy_service(): \n   %s\n   %s', name, opts)

        self._service.create_service(name, **opts)

        return self.get_service(name, version=opts.get('version'))
       
    def redeploy_service(self, name, **opts):
        """
        Updates properties on an existing web service on the ML Server by `name`
        and `version`. If `version=None` the most recent service will be
        updated.

        `Complete documentation <https://go.microsoft.com/fwlink/?linkid=
        836352>`_.

        **Example:**

        >>> opts = {
              'version': 'v1.0.0',
              'description': 'Service description.',
              'code_fn': run,
              'init_fn': init,
              'objects': {'local_obj': 50},
              'models': {'model': 100},
              'inputs': {'x': int},
              'outputs': {'answer': float},
              'artifacts': ['histogram.png'],
              'alias': 'consume_service_fn_alias'
            }
        >>> service = client.redeploy('regression', **opts)
        >>> res = service.consume_service_fn_alias(100)
        >>> answer = res.output('answer')
        >>> histogram = res.artifact('histogram.png')

        **NOTE:** Using `redeploy_service()` in this fashion is identical to
        updating a service using the fluent APIS
        :py:meth:`~azureml.deploy.operationalization.ServiceDefinition.redeploy`

        :param name: The web service name.
        :param opts: The service properties to update. `opts` dict supports the
               following optional properties:

               * version (str) - Defines a unique alphanumeric web service
                 version. If the version is left blank, a unique `guid` is
                 generated in its place. Useful during service development
                 before the author is ready to officially publish a semantic
                 version to share.
               * description (str) - The service description.
               * code_str (str) - A block of python code to run and evaluate.
               * init_str (str) - A block of python code to initialize service.
               * code_fn (function) - A Function to run and evaluate.
               * init_fn (function) - A Function to initialize service.
               * objects (dict) - Name and value of `objects` to include.
               * models (dict) - Name and value of `models` to include.
               * inputs (dict) - Service input schema by `name` and `type`.
                  The following types are supported:
                     - int
                     - float
                     - str
                     - bool
                     - numpy.array
                     - numpy.matrix
                     - numpy.DataFrame
               * outputs (dict) - Defines the web service output schema. If
                  empty, the service will not return a response value.
                  `outputs` are defined as a dictionary `{'x'=int}` or
                  `{'x': 'int'} that describes the output parameter names and
                  their corresponding data `types`.
                 The following types are supported:
                     - int
                     - float
                     - str
                     - bool
                     - numpy.array
                     - numpy.matrix
                     - numpy.DataFrame
               * artifacts (list) - A collection of file artifacts to return.
                 File content is encoded as a `Base64 String`.
               * alias (str) - The consume function name. Defaults to `consume`.
                  If `code_fn` function is provided, then it will use that
                  function name by default.

        :returns: A new instance of :class:`~.service.Service` representing the
                  service `deployed`.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """

        log.debug('MLServer.redeploy_service(): \n   %s\n   %s', name, opts)
    
        self._service.update_service(name, **opts)

        return self.get_service(name, version=opts.get('version'))

    def deploy_realtime(self, name, **opts):
        """
        Publish a new *realtime* web service on the ML Server by `name` and
        `version`.

        All input and output types are defined as a `pandas.DataFrame`.

        **Example:**

        >>> model = rx_serialize_model(model, realtime_scoring_only=True)
        >>> opts = {
               'version': 'v1.0.0',
               'description': 'Realtime service description.',
               'serialized_model': model
            }
        >>> service = client.deploy_realtime('scoring', **opts)
        >>> df = movie_reviews.as_df()
        >>> res = service.consume(df)
        >>> answer = res.outputs

        **NOTE:** Using `deploy_realtime()` in this fashion is identical to
        publishing a service using the fluent APIS
        :py:meth:`~azureml.deploy.operationalization.RealtimeDefinition.deploy`

        :param name: The web service name.
        :param opts: The service properties to publish. `opts` dict supports the
               following optional properties:

                * version (str) - Defines a unique alphanumeric web service
                  version. If the version is left blank, a unique `guid` is
                  generated in its place. Useful during service development
                  before the author is ready to officially publish a semantic
                  version to share.
                * description (str) - The service description.
                * alias (str) - The consume function name. Defaults to
                  `consume`.
        :returns: A new instance of :class:`~.service.Service` representing the
                  realtime service `redeployed`.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """
        log.debug('MLServer.deploy_realtime(): \n   %s\n   %s', name, opts)

        self._service.create_realtime(name, **opts)

        return self.get_service(name, version=opts.get('version'))

    def redeploy_realtime(self, name, **opts):
        """
        Updates properties on an existing *realtime* web service on the
        Server by `name` and `version`. If `version=None` the most recent
        service will be updated.

        All input and output types are defined as a `pandas.DataFrame`.

        **Example:**

        >>> model = rx_serialize_model(model, realtime_scoring_only=True)
        >>> opts = {
               'version': 'v1.0.0',
               'description': 'Realtime service description.',
               'serialized_model': model
            }
        >>> service = client.redeploy_realtime('scoring', **opts)
        >>> df = movie_reviews.as_df()
        >>> res = service.consume(df)
        >>> answer = res.outputs

        **NOTE:** Using `redeploy_realtime()` in this fashion is identical to
        updating a service using the fluent APIS
        :py:meth:`~azureml.deploy.operationalization.RealtimeDefinition.redeploy`

        :param name: The web service name.
        :param opts: The service properties to update. `opts` dict supports the
               following optional properties:

                * version (str) - Defines the web service version.
                * description (str) - The service description.
                * alias (str) - The consume function name. Defaults to
                  `consume`.
        :returns: A new instance of :class:`~.service.Service` representing the
                  realtime service `redeployed`.
        :raises HttpException: If a HTTP fault occurred calling the ML Server.
        """

        log.debug('MLServer.redeploy_realtime(): \n   %s\n   %s', name, opts)

        self._service.update_realtime_service(name, **opts)

        return self.get_service(name, version=opts.get('version'))
