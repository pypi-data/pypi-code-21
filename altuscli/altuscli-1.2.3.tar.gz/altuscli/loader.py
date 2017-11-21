# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import glob
import os

from altuscli import ALTUSCLI_ROOT
from altuscli.compat import json
from altuscli.compat import OrderedDict
from altuscli.exceptions import DataNotFoundError
from altuscli.exceptions import ValidationError
import yaml


def instance_cache(func):
    """Cache the result of a method on a per instance basis.

    This is not a general purpose caching decorator. In order for this to be used,
    it must be used on methods on an instance, and that instance *must* provide a
    ``self._cache`` dictionary.

    """
    def _wrapper(self, *args, **kwargs):
        key = (func.__name__,) + args
        for pair in sorted(kwargs.items()):
            key += pair
        if key in self._cache:
            return self._cache[key]
        data = func(self, *args, **kwargs)
        self._cache[key] = data
        return data
    return _wrapper


class JSONFileLoader(object):
    def exists(self, file_path):
        return os.path.isfile(file_path)

    def load_file(self, file_path):
        if not os.path.isfile(file_path):
            return

        # By default the file will be opened with locale encoding on Python 3.
        # We specify "utf8" here to ensure the correct behavior.
        with open(file_path, 'rb') as fp:
            payload = fp.read().decode('utf-8')
            return json.loads(payload, object_pairs_hook=OrderedDict)


class YAMLFileLoader(object):
    SERVICE_ALIAS_KEY = 'x-service-alias'

    def exists(self, file_path):
        return os.path.isfile(file_path)

    def load_file(self, file_path):
        if not os.path.isfile(file_path):
            return

        # By default the file will be opened with locale encoding on Python 3.
        # We specify "utf8" here to ensure the correct behavior.
        with open(file_path, 'rb') as fp:
            payload = fp.read().decode('utf-8')
            return self._ordered_load(payload)

    def load_alias(self, file_path):
        data = self.load_file(file_path)
        if data is not None and YAMLFileLoader.SERVICE_ALIAS_KEY in data:
            return data[YAMLFileLoader.SERVICE_ALIAS_KEY]

    def _ordered_load(self, stream):
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)


class Loader(object):
    """Find and load data models.

    This class will handle searching for and loading data models.

    """

    # The included models in altuscli/data/ that we ship with altuscli
    BUILTIN_DATA_PATH = os.path.join(ALTUSCLI_ROOT, 'data')
    # For convenience we automatically add ~/.altus/models to the data path.
    CUSTOMER_DATA_PATH = os.path.join(os.path.expanduser('~'), '.altus', 'models')

    def __init__(self):
        self._cache = {}
        # Note: the order of search paths determines the YAML file in case if file
        # names are the same (the first one wins). See self._service_directory method.
        self._search_paths = [self.CUSTOMER_DATA_PATH, self.BUILTIN_DATA_PATH]
        self._directory = self._service_directory()

    # returns a list of actual existing directories among search paths
    def _potential_locations(self):
        for path in self._search_paths:
            if os.path.isdir(path):
                yield path

    # lists potential service names in a given search path
    # which is obtained by sallow listing of subdirectories
    def _potential_services(self, path):
        for child in os.listdir(path):
            full_path = os.path.join(path, child)
            if os.path.isdir(full_path):
                yield (child, full_path)

    # build a 1:1 map of services to their YAML definition files
    # if multiple definitions are found in search path we will use one of them
    def _service_directory(self):
        dir = {}
        for possible_path in self._potential_locations():
            for (service_name, service_path) in self._potential_services(possible_path):
                for file in glob.glob(os.path.join(service_path, "*.yaml")):
                    # accumulate the last path in ascending lexical order,
                    # by filename (not full path) across all search paths
                    if service_name not in dir:
                        dir[service_name] = file
                    elif os.path.split(dir[service_name])[-1] != os.path.split(file)[-1]:
                        dir[service_name] = max(dir[service_name], file,
                                                key=lambda x: os.path.split(x)[-1])
        # expand aliases out of service models
        for service_name in list(dir.keys()):
            alias = YAMLFileLoader().load_alias(dir[service_name])
            if alias is not None:
                dir[alias] = dir[service_name]
        return dir

    # load the first json config file from one of search locations
    def load_json(self, name):
        loader = JSONFileLoader()
        for possible_path in self._potential_locations():
            full_path = os.path.join(possible_path, name)
            found = loader.load_file(full_path)
            if found is not None:
                return found
        raise DataNotFoundError(data_path=name)

    # returns a list of service names in directory
    def list_available_services(self):
        services = self._directory.keys()
        return sorted(services)

    # load YAML data by service name
    @instance_cache
    def load_service_data(self, service_name):
        if service_name not in self._directory.keys():
            raise ValidationError(value=service_name,
                                  param='service_name',
                                  type_name='str')
        return YAMLFileLoader().load_file(self._directory[service_name])
