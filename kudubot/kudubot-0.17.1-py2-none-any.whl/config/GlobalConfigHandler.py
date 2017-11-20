u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import with_statement
from __future__ import absolute_import
import os
import shutil
import logging
import importlib
from typing import List
from kudubot.services.BaseService import BaseService
from kudubot.exceptions import InvalidConfigException
from io import open


class GlobalConfigHandler(object):
    u"""
    Class that handles the global kudubot configuration
    files located in $HOME/.kudubot
    """

    logger = logging.getLogger(__name__)
    u"""
    The Logger for this class
    """

    def __init__(self,
                 config_location = os.path.join(
                     os.path.expanduser(u"~"), u".kudubot")
                 ):
        u"""
        Initializes the ConfigHandler.
        Determines the config locations using the config_location
        parameter which defaults to a .kudubot directory in the
        user's home directory.
        The configuration may still be invalid once the object is initialized,
        call validate_config_directory() to make sure
        that the configuration is correct.

        :param config_location: The location of the config directory
        """
        self.config_location = config_location
        self.global_connection_config_location = \
            os.path.join(self.config_location, u"connections.conf")
        self.services_config_location = \
            os.path.join(self.config_location, u"services.conf")
        self.data_location = os.path.join(self.config_location, u"data")
        self.specific_connection_config_location = \
            os.path.join(self.config_location, u"connection_config")
        self.external_services_directory = \
            os.path.join(self.config_location, u"external")
        self.external_services_executables_directory = \
            os.path.join(self.external_services_directory, u"bin")
        self.logfile_directory = os.path.join(self.config_location, u"logs")

    def validate_config_directory(self):
        u"""
        Validates the configuration directory.
        As soon as a discrepancy is detected, the reason is logged
        and False is returned. If the configuration is valid however,
        True is returned
        :return: True if the config is valid, False otherwise
        """

        try:
            if not os.path.isdir(self.config_location):
                raise InvalidConfigException(
                    u"Configuration directory " + self.config_location +
                    u" does not exist")
            elif not os.path.isfile(self.global_connection_config_location):
                raise InvalidConfigException(
                    u"Connection config file does not exist")
            elif not os.path.isfile(self.services_config_location):
                raise InvalidConfigException(
                    u"Services config file does not exist")
            elif not os.path.isdir(self.data_location):
                raise InvalidConfigException(
                    u"Data Location directory does not exist")
            elif not os.path.isdir(self.specific_connection_config_location):
                raise InvalidConfigException(
                    u"Connection Configuration directory does not exist")
            elif not os.path.isdir(self.external_services_directory):
                raise InvalidConfigException(
                    u"External Service directory does not exist")
            elif not os.path.isdir(
                    self.external_services_executables_directory):
                raise InvalidConfigException(
                    u"External Service executable directory does not exist")
            elif not os.path.isdir(self.logfile_directory):
                raise InvalidConfigException(
                    u"Log File Directory does not exist")
            else:
                self.logger.info(u"Configuration successfully checked")
                return True

        except InvalidConfigException, e:
            self.logger.warning(u"Configuration invalid: " + e.args[0])
            return False

    def generate_configuration(self, delete_old=False):
        u"""
        Generates a new, empty config location.

        :param delete_old: If set, all old config files
                           that may exist are overwritten
        :return: None
        """

        if delete_old and os.path.isdir(self.config_location):
            self.logger.info(u"Deleting old configuration files")
            shutil.rmtree(self.config_location)

        if not os.path.isdir(self.config_location):
            self.logger.info(u"Creating directory " + self.config_location)
            os.makedirs(self.config_location)

        if not os.path.isfile(self.global_connection_config_location):
            self.logger.info(
                u"Creating file " + self.global_connection_config_location)
            open(self.global_connection_config_location, u"w").close()

        if not os.path.isfile(self.services_config_location):
            self.logger.info(u"Creating file " + self.services_config_location)
            open(self.services_config_location, u"w").close()

        if not os.path.isdir(self.data_location):
            self.logger.info(u"Creating directory " + self.data_location)
            os.makedirs(self.data_location)

        if not os.path.isdir(self.specific_connection_config_location):
            self.logger.info(
                u"Creating directory " +
                self.specific_connection_config_location)
            os.makedirs(self.specific_connection_config_location)

        if not os.path.isdir(self.external_services_directory):
            self.logger.info(
                u"Creating directory " + self.external_services_directory)
            os.makedirs(self.external_services_directory)

        if not os.path.isdir(self.external_services_executables_directory):
            self.logger.info(
                u"Creating directory " +
                self.external_services_executables_directory)
            os.makedirs(self.external_services_executables_directory)

        if not os.path.isdir(self.logfile_directory):
            self.logger.info(u"Creating directory " + self.logfile_directory)
            os.makedirs(self.logfile_directory)

    def load_connections(self):
        u"""
        Loads all connections from the connections configuration file

        :return: A list of successfully imported Connection subclasses
        """
        from kudubot.connections.Connection import Connection

        self.logger.info(u"Loading connections")
        connections = self.__load_import_config__(
            self.global_connection_config_location, Connection)

        if len(connections) == 0:
            self.logger.warning(u"No connections loaded")

        return self.__remove_duplicate_services_or_connections__(connections)

    # noinspection PyUnresolvedReferences
    def load_services(self):
        u"""
        Loads all Services from the services configuration file

        :return: A list of successfully imported Service subclasses
        """
        self.logger.info(u"Loading Services")
        services = self.__load_import_config__(
            self.services_config_location, BaseService
        )

        # Check if dependencies for each service are satisfied
        # This loop structure is admittedly a bit weird,
        # but there's a valid reason!
        # Since we are removing Services with unsatisfied dependencies,
        # we need to re-check all
        # previous Services again if a Service is removed.
        # This is done by directly modifying the index variable i
        i = 0
        while i < len(services):

            service = services[i]

            for dependency in service.define_requirements():

                dependency_satisfied = False
                for other_service in services:
                    if other_service.define_identifier() == dependency:
                        dependency_satisfied = True
                        break

                if not dependency_satisfied:
                    self.logger.warning(
                        u"Dependency '" + dependency + u"' for service '" +
                        service.define_identifier() + u"' is not satisfied")
                    services.remove(service)
                    i = -1
                    break
            i += 1

        if len(services) == 0:
            self.logger.warning(u"No services loaded")

        return self.__remove_duplicate_services_or_connections__(services)

    # noinspection PyMethodMayBeStatic
    def __handle_import_statement__(self, statement):
        u"""
        Handles an import statement string

        :param statement: The import string to parse and execute
        :return: The retrieved class or module
        """

        for special_import, import_path in {
            u"NATIVE": u"from kudubot.services.native.",
            u"CONNECTION": u"from kudubot.connections."
        }.items():

            if statement.startswith(u"@" + special_import):

                try:
                    statement = statement.split(u"@" + special_import + u" ")[1]
                    module_name = statement.split(u"::")[0].strip()
                    class_name = statement.split(u"::")[1].strip()
                except IndexError:
                    raise ImportError(u"Failed to import " + special_import +
                                      u" module")

                statement = import_path + module_name + u"."
                statement += class_name + u" import " + class_name

        if statement.startswith(u"import"):
            return importlib.import_module(statement.split(u"import ", 1)[1])
        else:
            statement = statement.split(u"from ", 1)[1]
            statement = statement.split(u" import ")
            _module = importlib.import_module(statement[0])
            return getattr(_module, statement[1])

    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def __remove_duplicate_services_or_connections__(self, target):
        u"""
        Removes any duplicate Connections or Services from a list

        :param target: The list to remove the duplicates from
        :return: The list with duplicates removed
        """

        results = []

        for element in target:

            hitcount = 0

            for other in target:
                if other.define_identifier() == element.define_identifier():
                    hitcount += 1

            if hitcount == 1:
                results.append(element)
            else:

                exists = False

                for result in results:
                    if result.define_identifier() ==\
                            element.define_identifier():
                        exists = True
                        break

                if not exists:
                    results.append(element)

        return results

    # noinspection PyMethodMayBeStatic
    def __load_import_config__(self, file_location, class_type):
        u"""
        Reads an import config file
        (A file containing only python import statements)
        and returns a list of the successful imports.

        Imports that fail are simply ignored,
        as well as those that do not return subclasses
        of the class_type parameter.

        :param file_location: The import config file's location
        :param class_type: The class type all imports must subclass
        :return: The list of successful imports
        """

        modules = []

        with open(file_location, u'r') as config:
            content = config.read().split(u"\n")

        for line in content:

            self.logger.debug(u"Trying to import '" + line + u"'")

            if line.strip().startswith(u"#") or line == u"":
                self.logger.debug(u"Skipping line: " + line + u"")
                continue
            else:
                try:
                    _module = self.__handle_import_statement__(line)

                    if issubclass(_module, class_type):
                        modules.append(_module)
                        self.logger.info(u"Import " + line + u" successful")
                    else:
                        self.logger.warning(
                            u"Import " + line + u" is not of type " +
                            unicode(class_type)
                        )

                except (ImportError, AttributeError):  # Ignore invalid imports
                    self.logger.warning(u"Import " + line + u" has failed")
                except IndexError:  # Ignore failed parsing attempts
                    self.logger.warning(
                        u"Import " + line +
                        u" has failed due to an error in the config file."
                    )

        return modules

    def delete_service_executables(self):
        u"""
        Deletes all executable service files

        :return: None
        """
        shutil.rmtree(self.external_services_executables_directory)
        os.makedirs(self.external_services_executables_directory)
