"""Tools for shimming the JSON output from validate_drp into the simpler
JSON schema expected by the SQuaSH dashboard's POST /api/jobs/ endpoint.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA


def shim_validate_drp(vdrp_json, registered_metrics=[]):
    """Convert JSON structure from validate DRP into the JSON documents
    expected by SQuaSH's API.

    Populates the ``blobs`` and ``measurements`` fields of the job document
    expected by the api/jobs endpoint.

    For metrics not registered in SQuaSH, makes a metric document as
    expected by the api/metrics endpoint.
    """

    job_json = {
        'blobs': vdrp_json['blobs']
    }

    new_metrics_json = []
    measurements = []
    for vdrp_measurement_doc in vdrp_json['measurements']:
        if vdrp_measurement_doc['value'] is None:
            continue
        if vdrp_measurement_doc['metric']['name'] not in registered_metrics:
            new_metrics_json.append(shim_metric_definition(vdrp_measurement_doc))
            # Make sure a given metric is appended just once,
            # uniqueness constraint, see DM-9330
            registered_metrics.append(vdrp_measurement_doc['metric']['name'])
        measurements.append(shim_vdrp_measurement(vdrp_measurement_doc))

    metric_json = new_metrics_json
    job_json['measurements'] = measurements

    return metric_json, job_json


def shim_vdrp_measurement(vdrp_measurement_doc):
    """Shim a measurement document from validate_drp to a measurement document
    expected by SQuaSH.
    """
    # Metric definition is handled in the metric document
    metric = vdrp_measurement_doc.pop('metric')

    # Value is stored in a separate field and the rest of the measurement
    # document is stored as metadata in SQuaSH
    # http://sqr-009.lsst.io/en/latest/
    value = vdrp_measurement_doc.pop('value')

    output_doc = {
        'metric': metric['name'],
        'value': value,
        'metadata': vdrp_measurement_doc
    }
    return output_doc


def shim_metric_definition(vdrp_measurement_doc):
    """Convert JSON structure in validate DRP into the JSON expected
    by SQuaSH for metric definition.
    """
    metric = vdrp_measurement_doc['metric']

    metric_json = {
        'metric': metric['name'],
        'description': metric['description'],
        'reference': metric['reference'],
        'specs': metric['specifications'],
        'operator': metric['operator_str'],
        'parameters': metric['parameters'],
        # FIXME Unit is being stored as part of the metric definition
        # in SQuaSH, see DM-9312
        'unit': vdrp_measurement_doc['unit']
    }
    return metric_json
