# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
Role
====

`Operationalization` is designed to be a low-level abstract foundation class 
from which other service operationalization attribute classes in the `mldeploy` 
package can be derived. It provides a standard template for creating
attribute-based operationalization lifecycle phases providing a consistent 
`__init()__`, `__del()__` sequence that chains initialization (initializer),
authentication (authentication), and destruction (destructor) methods for the 
class hierarchy.
"""

import collections

# python 2 and python 3 compatibility library
from six import add_metaclass, iteritems
from abc import ABCMeta, abstractmethod


@add_metaclass(ABCMeta)
class Operationalization(object):
    """
    `Operationalization` is designed to be a low-level abstract foundation class
    from which other service operationalization attribute classes in the
    `mldeploy` package can be derived. It provides a standard template for
    creating attribute-based operationalization lifecycle phases providing a
    consistent  `__init()__`, `__del()__` sequence that chains initialization
    (initializer), authentication (authentication), and destruction (destructor)
    methods for the class hierarchy.
    """
    
    def __init__(self):        
        pass

    def initializer(self, api_client, config):
        """
        Init lifecycle method, invoked during construction. Sets up attributes 
        and invokes initializers for the class hierarchy.

        An optional _noonp_ method where subclass implementers MAY provide this 
        method definition by overriding.

        Object with configuration property name/value pairs
        """
        pass
        
    def destructor(self):
        """
        Destroy lifecycle method. Invokes destructors for the class hierarchy.

        An optional _noonp_ method where subclass implementers MAY provide this 
        method definition by overriding.
        """        
        pass
        
    def authentication(self, context):
        """
        Authentication lifecycle method. Invokes the authentication entry-point
        for the class hierarchy.        

        An optional _noonp_ method where subclass implementers MAY provide this 
        method definition by overriding.
        """         
        pass
        
    @abstractmethod
    def get_service(self, name):
        """
        Retrieve service meta-data from the name source and return an new
        service instance.

        Sub-class should override.
        """

    @abstractmethod
    def list_services(self, name=None, **opts):
        """
        Sub-class should override.
        """

    @abstractmethod
    def delete_service(self, name):
        """
        Sub-class should override.
        """     

    @abstractmethod
    def deploy_service(self, name, **opts):
        """
        Sub-class should override.
        """

    @abstractmethod
    def redeploy_service(self, name, force=False, **opts):
        """
        Sub-class should override.
        """

    @abstractmethod
    def deploy_realtime(self, name, **opts):
        """
        return a new service instance.
        """

    @abstractmethod
    def redeploy_realtime(self, name, force=False, **opts):
        """
        return a new service instance.
        """
        
    def service(self, name):
        """
        Begin fluent API for defining a web service.

        **Example:**

        >>> client.service('scoring')
              .description('A new web service')
              .version('v1.0.0')

        :param name: The web service name.
        :returns: A :class:`~.ServiceDefinition` for fluent API.
        """

        return ServiceDefinition(name, self)

    def realtime_service(self, name):
        """
        Begin fluent API for defining a realtime web service.

        **Example:**

        >>> client.realtime_service('scoring')
              .description('A new realtime web service')
              .version('v1.0.0')

        :param name: The web service name.
        :returns: A :class:`~.RealtimeDefinition` for fluent API.
        """
        return RealtimeDefinition(name, self)

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


@add_metaclass(ABCMeta)
class OperationalizationDefinition(object):
    """
    Base abstract class defining a service's properties on the fluent API.
    """
    def __init__(self, name, op, defs_extent={}):
        """
        Create a new publish definition.

        :param name: The web service name
        :param op:
        :param defs_extent:
        """
        self._name = name
        self._op = op
        self._defs = {
            'version': None,
            'alias': None,
            'description': None
        }

        self._defs.update(defs_extent)

    def version(self, version):
        """
        Set the service version.

        :param version:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        self._defs['version'] = version
        return self

    def alias(self, alias):
        """
        Set the service function name alias to call.

        :param alias:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        self._defs['alias'] = alias
        return self        

    def description(self, description):
        """
        Set the service description.

        :param description:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """

        self._defs['description'] = description
        return self

    @abstractmethod
    def deploy(self):
        """
        Bundle up the definition properties and publish the service.
        :return:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        pass

    @abstractmethod
    def redeploy(self, force=False):
        """
        Bundle up the definition properties and update the service.
        To be implemented by subclasses.

        :param force:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        pass

    @abstractmethod
    def __str__(self):        
        pass

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class ServiceDefinition(OperationalizationDefinition):
    """
    Service class defining a service's properties on the fluent API.
    """
    def __init__(self, name, op):
        defs_extent = {
            'code_str': None,
            'init_str': None,
            'code_fn': None,
            'init_fn': None,
            'objects': None,
            'models': None,
            'inputs': None,
            'outputs': None,
            'artifacts': None
        }

        super(ServiceDefinition, self).__init__(name, op, defs_extent)

    def code_str(self, code, init=None):
        """
        Set the service consume function as a block of python code.

        :param code:
        :param init:
        :returns: A :class:`~.ServiceDefinition` for fluent API.
        """
        self._defs['code_str'] = code
        self._defs['init_str'] = init

        return self

    def code_fn(self, code, init=None):
        """
        Set the service consume function as a function.
        :param code:
        :param init:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """

        self._defs['code_fn'] = code
        self._defs['init_fn'] = init

        return self

    def objects(self, **objects):
        """
        Objects.

        :param objects:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if objects is None:
            return self

        self._update('objects', objects)

        return self

    def models(self, **models):
        """
        Models.

        :param models:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if models is None:
            return self

        self._update('models', models)

        return self

    def inputs(self, **inputs):
        """
        Defines inputs.

        :param inputs:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if inputs is None:
            return self

        if self._defs['inputs'] is None:
            self._defs['inputs'] = collections.OrderedDict()

        self._update('inputs', inputs)

        return self

    def outputs(self, **outputs):
        """
        Defines utputs.

        :param outputs:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if outputs is None:
            return self

        if self._defs['outputs'] is None:
            self._defs['outputs'] = collections.OrderedDict()

        self._update('outputs', outputs)

        return self

    def artifacts(self, artifacts):
        """
        File artifacts.

        :param artifacts:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if artifacts is None:
            return self

        if self._defs['artifacts'] is None:
            self._defs['artifacts'] = []

        self._defs['artifacts'].extend(artifacts)

        return self

    def artifact(self, artifact):
        """
        A single File artifact.

        :param artifact:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if artifact is None:
            return self

        self.artifacts([artifact])

        return self

    def deploy(self):
        """
        Bundle up the definition properties and publish the service.

        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        return self._op.deploy_service(self._name, **self._defs)

    def redeploy(self, force=False):
        """
        Bundle up the definition properties and update the service.

        :param force:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        return self._op.redeploy_service(self._name, **self._defs)

    def _update(self, prop, dictionary):
        if dictionary is None or not isinstance(dictionary, dict):
            raise ValueError('A valid `dictionary` is required for "{0}"'.
                             format(prop))

        if self._defs[prop] is None:
            self._defs[prop] = {}

        for key, value in iteritems(dictionary):
            self._defs[prop][key] = value

    def __str__(self):
        return '<ServiceDefinition>\n' \
               '   name: {name}\n' \
               '   version: {version}\n' \
               '   code_fn: {code_fn}\n' \
               '   init_fn: {init_fn}\n' \
               '   code_str: {code_str}\n' \
               '   init_str: {init_str}\n' \
               '   objects: {objects}\n' \
               '   models: {models}\n' \
               '   inputs: {inputs}\n' \
               '   outputs: {outputs}\n' \
               '   artifacts: {artifacts}\n' \
               '   alias: {alias}\n' \
               '   description: {description}'. \
            format(name=self._name, **self._defs)

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class RealtimeDefinition(OperationalizationDefinition):
    """
    Realtime class defining a service's properties on the fluent API.
    """
    def __init__(self, name, op):
        """
        Defines a realtime service publish definition.

        :param name:
        :param op:
        """
        defs_extent = {
            'serialized_model': None
        }
        super(RealtimeDefinition, self).__init__(name, op, defs_extent)

    def serialized_model(self, model):
        """
        Serialized model.

        :param model:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        if model is None: return self
        if self._defs['serialized_model'] is None:
            self._defs['serialized_model'] = model
        else:
            raise ValueError('The realtime service should have one and only one'
                             ' model.')
        return self

    def deploy(self):
        """
        Bundle up the definition properties and publish the service.

        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        return self._op.deploy_realtime(self._name, **self._defs)

    def redeploy(self, force=False):
        """
        Bundle up the definition properties and update the service.

        :param force:
        :returns: Self :class:`~.OperationalizationDefinition` for fluent API.
        """
        return self._op.redeploy_realtime(self._name, **self._defs)

    def __str__(self):
        return '<RealtimeDefinition>\n' \
               '   name: {name}\n' \
               '   version: {version}\n' \
               '   serialized_model: {serialized_model}\n' \
               '   alias: {alias}\n' \
               '   description: {description}'. \
            format(name=self._name, **self._defs)
