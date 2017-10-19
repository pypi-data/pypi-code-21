# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os.path

templates_directory = os.path.join(os.path.dirname(__file__), 'templates')


def generate_service_swagger(service_name, service_schema_file_path=None,
                             service_version="1.0", service_path_prefix=''):
    spec_template_file_path = os.path.join(templates_directory, 'swagger_template.json')
    with open(spec_template_file_path, 'r') as f:
        swagger_spec_str = f.read()

    # empty string is fine. ending slash is not.
    if service_path_prefix and not service_path_prefix.startswith('/'):
        service_path_prefix = '/{}'.format(service_path_prefix)
    service_path_prefix = service_path_prefix.rstrip('/')

    # string replace since we're replacing some keys now as well
    swagger_spec_str = swagger_spec_str\
        .replace("$SERVICE_NAME$", service_name)\
        .replace("$SERVICE_VERSION$", service_version)\
        .replace('$PATH_PREFIX$', service_path_prefix)
    swagger_spec_json = json.loads(swagger_spec_str)

    # if service schema is present, use that to define the service's data contracts
    if service_schema_file_path:
        if not (os.path.exists(service_schema_file_path) and os.path.isfile(service_schema_file_path)):
            raise ValueError("Invalid service schema file path: {0}. The path doesn't exist or is not a file.".format(
                service_schema_file_path))

        with open(service_schema_file_path, 'r') as f:
            service_schema_json = json.load(f)

        if "input" in service_schema_json:
            swagger_spec_json["definitions"]["ServiceInput"] = _get_service_input_output_swagger(
                service_schema_json["input"])
        if "output" in service_schema_json:
            swagger_spec_json["definitions"]["ServiceOutput"] = _get_service_input_output_swagger(
                service_schema_json["output"])

    return swagger_spec_json


def _get_service_input_output_swagger(generated_schema):
    swagger_def = {"type": "object", "properties": {}, "example": {}}
    for item_name in generated_schema:
        if "swagger" not in generated_schema[item_name]:
            raise ValueError("Missing swagger schema for item with name={}".format(item_name))
        item_swagger = copy.deepcopy(generated_schema[item_name]["swagger"])
        swagger_def["example"][item_name] = item_swagger["example"]
        del item_swagger["example"]
        swagger_def["properties"][item_name] = item_swagger
    return swagger_def
