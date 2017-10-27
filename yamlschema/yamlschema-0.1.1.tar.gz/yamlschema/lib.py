"""
Validate a YAML config file
"""

import os
import sys

import yaml

from jsonschema import validate, ValidationError, FormatChecker

from codado.tx import Main


class ValidateConfig(Main):
    """
    Validate config.yml based on config.schema.yml
    """
    synopsis = "path/to/config.yml path/to/schema.yml"
    optFlags = [
        ['schema', None, 'Display normalized schema from file']
    ]
    optParameters = []

    def parseArgs(self, configFile, configSchema):
        if not os.access(configFile, os.R_OK):
            raise OSError("Cannot read config file %s" % configFile)
        if not os.access(configSchema, os.R_OK):
            raise OSError("Cannot read schema file %s" % configSchema)

        self['configFile'] = configFile
        self['configSchema'] = configSchema

    def postOptions(self):
        """
        Validate config file
        """
        print >>sys.stderr, "Validating {}\n".format(self['configFile'])
        res = validateConfig(self['configFile'], self['configSchema'])
        print >>sys.stderr, "{} is valid\n".format(self['configFile'])
        return res


def validateConfig(configYML, configSchemaYML):
    """
    Validate configYML based off of configSchemaYML
    """
    config = yaml.load(open(configYML))
    schema = yaml.load(open(configSchemaYML))
    try:
        validate(config, schema, format_checker=FormatChecker())
        return True
    except ValidationError, ve:
        raise ve