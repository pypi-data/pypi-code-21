#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: chanconfig/config.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
import logging
import pkg_resources
import yaml

from attrdict import AttrDict
from yaml.parser import ParserError


class Config(object):
    """Class for reading and parsing configurations from yaml file
    """
    def __init__(self, path, package=None):
        """Initialize class with given path and optional package name.

        Args:
            path: a str
            package: a str, default None
        """
        logger = logging.getLogger(__name__)

        if package:
            try:
                path = pkg_resources.resource_filename(package, path)
            except ImportError as error:
                logger.exception(error)
                raise ReadConfigurationError(path, str(error))

        try:
            with open(path) as ymlfile:
                self._dict = AttrDict(yaml.load(ymlfile))
        except (IOError, ParserError) as error:
            logger.exception(error)
            raise ReadConfigurationError(path, str(error))

        logger.info('Successfully read configurations from {0}'.format(path))

    def __getattr__(self, name):
        return getattr(self._dict, name)

    def __eq__(self, other):
        return self._dict == other

    def __repr__(self):
        return str(self._dict)

    def update(self, update_dict):
        """Update values from another dict

        Args:
            update_dict: a ``dict``
        """
        self._dict += update_dict


class ReadConfigurationError(Exception):
    """Exception class for errors in reading configuration
    """
    def __init__(self, path, info):
        """Initialization

        Args:
            path: a str, the configs path
            info: a str, the error info
        """
        self.path = path
        self.info = info

    def __repr__(self):
        return '{0}: {1} {2}'.format(
            self.__class__.__name__, self.path, self.info
        )

    def __str__(self):
        return 'Read {0} error: {1}'.format(self.path, self.info)
