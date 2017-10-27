

import os
import sys

import yaml

from jsonschema import validate, ValidationError, FormatChecker

from codado.tx import Main


class ValidateConfig(Main):
    """
    Validate that config.yml is valid based on config.schema.yml
    """
    synopsis = "path/to/config.yml | --schema path/to/schema.yml"
    optFlags = [
        ['schema', None, 'Display normalized schema from file']
    ]
    optParameters = []

    def parseArgs(self, configFile=DEFAULT_CONFIG):
        if not os.access(configFile, os.R_OK):
            raise OSError("Cannot read config or schema file %s" % configFile)
        self['configFile'] = configFile

    def postOptions(self):
        """
        Validate config file
        """
        if self['schema']:
            print >>sys.stderr, "Output {}\n".format(self['configFile'])
            with open(self['configFile']) as f:
                res = yaml.dump(yaml.load(f))
                print res
                return res
        else:
            print >>sys.stderr, "Validating {}\n".format(self['configFile'])
            res = validateConfig(self['configFile'])
            print >>sys.stderr, "{} is valid\n".format(self['configFile'])
            return res


def validateConfig(configYML, configSchemaYML):
    """
    Validate that values in a config file are valid
    """

    config = yaml.load(open(configYML))
    schema = yaml.load(open(configSchemaYML))
    try:
        validate(config, schema, format_checker=FormatChecker())
        return True
    except ValidationError, ve:
        raise ve