from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import json
import pkg_resources

import jsonschema


def validate(doc, schema):
    """Validate a document against a schema.

    This function ensures that additional format checkers (for datetime
    and URIs) are active.
    """
    format_checker = jsonschema.FormatChecker()
    jsonschema.validate(doc, schema, format_checker=format_checker)


def load_schema(schema):
    """Load JSON schema for a SQUASH metric upload."""
    data = pkg_resources.resource_string(__name__,
                                         'schemas/{}.json'.format(schema))
    return json.loads(data.decode('utf-8'))


def load_squash_measurements_schema():
    """Load JSON schema for the **measurements** object in a SQUASH job upload.
    """
    job_schema = load_schema(schema='job')

    m_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "SQUASH Job upload schema",
        "description": "This JSON schema applies POST https://squash.lsst.codes/api/jobs.",  # noqa
    }
    m_schema['definitions'] = job_schema['definitions']
    m_schema.update(job_schema['definitions']['measurements'])

    return m_schema


def load_squash_packages_schema():
    """Load JSON schema for the **packages** object in a SQUASH job upload.
    """
    job_schema = load_schema(schema='job')

    m_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "SQUASH Job upload schema",
        "description": "This JSON schema applies POST https://squash.lsst.codes/api/jobs.",  # noqa
    }
    m_schema['definitions'] = job_schema['definitions']
    m_schema.update(job_schema['definitions']['packages'])

    return m_schema
