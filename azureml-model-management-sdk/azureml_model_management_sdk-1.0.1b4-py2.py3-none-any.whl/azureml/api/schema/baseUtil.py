# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import abc
import base64


class BaseUtil(object):
    __metaclass__ = abc.ABCMeta

    MAX_RECORDS_FOR_SAMPLE_SCHEMA = 3

    @classmethod
    @abc.abstractmethod
    def extract_schema(cls, data):
        pass

    @classmethod
    @abc.abstractmethod
    def get_input_object(cls, input, schema):
        pass

    @classmethod
    def get_swagger_sample(cls, iterable_records, max_count, item_schema):
        sample_swagger = []
        for i in range(max_count):
            item_sample = cls._get_data_record_swagger_sample(item_schema, iterable_records[i])
            sample_swagger.append(item_sample)
        return sample_swagger

    @classmethod
    @abc.abstractmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        pass

    @staticmethod
    def _validate_schema_object_property(schema, property_name, schema_file):
        if property_name not in schema \
                or schema[property_name] is None\
                or len(schema[property_name]) == 0:
            err = "Invalid schema file - {0}:  the {1} property must be specified.".format(schema_file, property_name)
            raise ValueError(err)

    @classmethod
    def _get_data_record_swagger_sample(cls, item_swagger_schema, data_item):
        item_type = item_swagger_schema['type']
        if item_type == 'object':
            if 'properties' in item_swagger_schema:
                sample_swag = dict()
                for field in item_swagger_schema['properties']:
                    sample_swag[field] = cls._get_data_record_swagger_sample(
                        item_swagger_schema['properties'][field], data_item[field])
            elif 'additionalProperties' in item_swagger_schema:
                sample_swag = dict()
                for field in data_item:
                    sample_swag[field] = cls._get_data_record_swagger_sample(
                        item_swagger_schema['additionalProperties'], data_item[field])
            else:
                sample_swag = str(data_item)
        elif item_swagger_schema['type'] == 'array':
            sample_swag = []
            subarray_item_swagger = item_swagger_schema['items']
            for i in range(len(data_item)):
                array_item_sample = cls._get_data_record_swagger_sample(
                    subarray_item_swagger, data_item[i])
                sample_swag.append(array_item_sample)
        elif item_type == 'number':
            sample_swag = float(data_item)
        elif item_type == 'integer':
            sample_swag = int(data_item)
        elif item_type == 'bool':
            sample_swag = bool(data_item)
        elif item_type == 'string' and 'format' in item_swagger_schema:
            if item_swagger_schema['format'] == 'date':
                sample_swag = cls._date_item_to_string(data_item)
            elif item_swagger_schema['format'] == 'date-time':
                sample_swag = cls._timestamp_item_to_string(data_item)
            elif item_swagger_schema['format'] == 'binary':
                sample_swag = base64.b64encode(data_item).decode('utf-8')
            else:
                sample_swag = str(data_item)
        else:
            sample_swag = str(data_item)
        return sample_swag

    @classmethod
    @abc.abstractmethod
    def _preprocess_json_input(cls, json_input, item_schema):
        pass

    @classmethod
    @abc.abstractmethod
    def _date_item_to_string(cls, date_item):
        pass

    @classmethod
    @abc.abstractmethod
    def _timestamp_item_to_string(cls, date_item):
        pass
