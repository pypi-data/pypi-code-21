"""
Patch boto3 functionality so that you can retrieve the arn
from any given resource instance
"""

import boto3
import os
from boto3.exceptions import ResourceLoadException
from boto3.resources.model import ResourceModel
from string import Formatter

import inspect
import logging

logger = logging.getLogger(__name__)


class ServiceContext(object):
    def __init__(self,
                 service_name,
                 service_model,
                 service_waiter_model,
                 resource_json_definitions,
                 session=None):
        self._service_name = service_name
        self._service_model = service_model
        self._service_waiter_model = service_waiter_model
        self._resource_json_definitions = resource_json_definitions
        self._session = session
        if not self._session:
            # HACK: this is very brittle and should idealy be fixed with an
            # upstream patch https://github.com/boto/boto3/pull/898
            # TODO: make sure the caller is in fact a Session object
            session = inspect.currentframe().f_back.f_locals['self']
            if session is None:
                raise Exception('Unable to get session from stack frame.')
            else:
                self._session = session

    @property
    def service_name(self):
        return self._service_name

    @property
    def service_model(self):
        return self._service_model

    @property
    def service_waiter_model(self):
        return self._service_waiter_model

    @property
    def resource_json_definitions(self):
        return self._resource_json_definitions

    @property
    def session(self):
        return self._session


class PatchedResourceFactory(boto3.resources.factory.ResourceFactory):
    def load_from_definition(self, *args, **kwargs):
        service_context = kwargs['service_context']
        cls = boto3.resources.factory.ResourceFactory.load_from_definition(
            self, *args, **kwargs)
        cls.meta.session = service_context._session
        attrs = {'meta': cls.meta}

        service_name = service_context.service_name
        resource_name = kwargs['resource_name']
        api_version = None  # TODO: multiple arn versions?
        loader = service_context._session._loader

        # Ensure the boto3-arn-patch data directory
        # is in the loader search path
        loader.search_paths.append(os.path.join(
            os.path.dirname(__file__), 'data'))

        arn_model = loader.load_service_model(service_name,
                                              'arns-1',
                                              api_version)

        arn_model = arn_model.get('resources', {}).get(resource_name, {})

        self._load_arn(attrs, cls.meta, arn_model)
        cls = type(cls.__name__, (cls, ), attrs)
        return cls

    def _load_arn(self, attrs, meta, arn_model):
        arn_config = arn_model.get('arn', False)

        # Only define an arn if the resource has a defined arn format
        if arn_config:
            arn_property = None
            format_string = arn_config.get('formatString', False)
            data_path = arn_config.get('dataPath', False)

            if format_string:

                def construct_arn(self):
                    formatter = Formatter()
                    mapping = {}
                    keys = [k[1] for k in formatter.parse(format_string)
                            if k[1]]
                    keys = set(keys)

                    if 'partition' in keys:
                        keys.remove('partition')
                        mapping['partition'] = self.meta.client.meta.partition
                    if 'service' in keys:
                        keys.remove('service')
                        mapping['service'] = self.meta.service_name
                    if 'region' in keys:
                        keys.remove('region')
                        mapping['region'] = self.meta.session.region_name
                    if 'account-id' in keys:
                        keys.remove('account-id')
                        mapping['account-id'] = self.meta.session.account_id

                    # Currently supports account of only top level properties
                    for key in keys:
                        mapping[key] = getattr(self, key)
                        # TODO error handling
                    return format_string.format(**mapping)

                arn_property = property(construct_arn)
            elif data_path:

                def arn_path_loader(self):
                    if self.meta.data is None:
                        if hasattr(self, 'load'):
                            self.load()
                        else:
                            raise ResourceLoadException(
                                '{0} has no load method'.format(
                                    self.__class__.__name__))

                    data = self.meta.data
                    for key in data_path:
                        data = data[key]  # TODO: Error handling
                    return data

                arn_property = property(arn_path_loader)

            if not (arn_property):
                raise (NotImplementedError)

            # Rename arn if an attribute already exists
            key = '_arn' if 'arn' in attrs else 'arn'
            attrs[key] = arn_property


class PatchedResourceMeta(boto3.resources.base.ResourceMeta):
    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        self.session = session


def patch_session():
    @property
    def account_id(self):
        """
        The **read-only** account id.
        """
        try:
            return self._account_id
        except AttributeError:
            # TODO: Error handling
            account_id = self.client('sts').get_caller_identity()['Account']
            self._account_id = account_id
        return self._account_id

    logger.info('Patching Session.account_id')
    boto3.Session.account_id = account_id


def patch_service_context():
    logger.info('Patching ServiceContext')
    boto3.utils.ServiceContext = ServiceContext


def patch_resource_factory():
    logger.info('Patching ResourceFactory')
    boto3.session.ResourceFactory = PatchedResourceFactory


def patch_resource_meta():
    logger.info('Patching ResourceMeta')
    boto3.resources.factory.ResourceMeta = PatchedResourceMeta
    boto3.resources.base.ResourceMeta = PatchedResourceMeta