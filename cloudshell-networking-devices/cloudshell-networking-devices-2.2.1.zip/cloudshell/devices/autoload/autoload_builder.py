#!/usr/bin/python
# -*- coding: utf-8 -*-

import posixpath

from cloudshell.shell.core.driver_context import AutoLoadDetails, AutoLoadAttribute, AutoLoadResource


class AutoloadDetailsBuilder(object):
    def __init__(self, autoload_data):
        """
        :param autoload_data: dict(defaultdict(list)):
        """

        self.autoload_data = autoload_data
        self._autoload_details = AutoLoadDetails([], [])

    def autoload_details(self):
        self._build_autoload_details(self.autoload_data)
        return self._autoload_details

    @staticmethod
    def _validate_build_resource_structure(autoload_resource):
        """Validate resource structure

        :param dict autoload_resource:
        :return correct autoload resource structure
        :rtype: dict
        """
        result = {}

        for resource_prefix, resources in autoload_resource.iteritems():

            max_free_index = max(map(int, resources)) + 1 or 1

            for index, sub_resources in resources.iteritems():
                if not index or index == -1:
                    index = max_free_index
                    max_free_index += 1

                if len(sub_resources) > 1:
                    result["{0}{1}".format(resource_prefix, index)] = sub_resources[0]
                    for resource in sub_resources[1:]:
                        result["{0}{1}".format(resource_prefix, str(max_free_index))] = resource
                        max_free_index += 1
                else:
                    result["{0}{1}".format(resource_prefix, index)] = sub_resources[0]

        return result

    def _build_autoload_details(self, autoload_data, relative_path=""):
        """ Build autoload details

        :param autoload_data: dict:
        :param relative_path: str: full relative path of current autoload resource
        """

        self._autoload_details.attributes.extend([AutoLoadAttribute(relative_address=relative_path,
                                                                    attribute_name=attribute_name,
                                                                    attribute_value=attribute_value)
                                                  for attribute_name, attribute_value in
                                                  autoload_data.attributes.iteritems()])

        for resource_relative_path, resource in self._validate_build_resource_structure(autoload_data.resources).iteritems():
            full_relative_path = posixpath.join(relative_path, resource_relative_path)
            self._autoload_details.resources.append(AutoLoadResource(model=resource.cloudshell_model_name,
                                                                     name=resource.name,
                                                                     relative_address=full_relative_path,
                                                                     unique_identifier=resource.unique_identifier))

            self._build_autoload_details(autoload_data=resource, relative_path=full_relative_path)
