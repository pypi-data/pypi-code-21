"""
Utilities for working with configuration
"""
import base64
import io
import json
import os

import boto3
import jsonpointer

def create_config_client(config_provider, config_source):
    """
    Create a config client of the specified type
    """
    if config_provider == 'environment' or config_provider is None:
        return EnvironmentVariableConfigClient()

    elif config_provider == 'aws_ssm':
        return SsmConfigClient(config_source)

    elif config_provider == 'aws_s3':
        return S3ConfigClient(config_source)

    elif config_provider == 'local_json_file':
        return LocalJsonFileConfigClient(config_source)

    else:
        raise RuntimeError("Invalid config provider: {0}".format(config_provider))

def create_config_client_v2(config_source):
    provider, source = config_source.split(":")
    return create_config_client(provider, source)

def create_common_config_client(config_prefix, config_name, config_provider='aws_ssm'):
    config_source = "/{0}/{1}/config".format(config_prefix, config_name)
    return create_config_client(config_provider, config_source)

class BaseConfigClient(object):
    def get_value(self, parameter_path):
        raise NotImplementedError()

    def get_pointer_value(self, pointer):
        raise NotImplementedError()

    def get_root_json_value(self):
        raise NotImplementedError()

    def get_child_config_client(self, config_source_pointer):
        return create_config_client_v2(self.get_pointer_value(config_source_pointer))

    def get_child_config(self, config_source_pointer):
        child_config_client = create_config_client_v2(self.get_pointer_value(config_source_pointer))
        return child_config_client.get_root_json_value()

class EnvironmentVariableConfigClient(BaseConfigClient):
    """
    """
    def get_value(self, parameter_path):
        return os.environ[parameter_path.upper()]

class SsmConfigClient(BaseConfigClient):
    """
    """
    def __init__(self, config_source):
        self.ssm_client = boto3.client('ssm')

        self.config_source = config_source

    def get_value(self, parameter_path):
        data = self.get_root_json_value()
        return data[parameter_path]

    def get_pointer_value(self, pointer):
        data = self.get_root_json_value()
        return jsonpointer.resolve_pointer(data, pointer)

    def get_root_json_value(self):
        response = self.ssm_client.get_parameter(
            Name=self.config_source,
            WithDecryption=True
        )

        return json.loads(base64.b64decode(response['Parameter']['Value']).decode())

class S3ConfigClient(BaseConfigClient):
    """
    """
    def __init__(self, config_source):
        self.s3_client = boto3.client('s3')

        self.bucket, self.key = config_source.split("/", 1)

    def get_value(self, parameter_path):
        data = self.get_root_json_value()
        return data[parameter_path]

    def get_pointer_value(self, pointer):
        data = self.get_root_json_value()
        return jsonpointer.resolve_pointer(data, pointer)

    def get_root_json_value(self):
        buffer = io.BytesIO()
        self.s3_client.download_fileobj(self.bucket, self.key, buffer)
        json_string = buffer.getvalue().decode()
        return json.loads(json_string)

class LocalJsonFileConfigClient(BaseConfigClient):
    """
    Config client reading config from a local JSON file
    """
    def __init__(self, config_source):
        with open(config_source) as json_file:
            self.config = json.load(json_file)

    def get_value(self, parameter_path):
        return self.config[parameter_path]

    def get_root_json_value(self):
        return self.config

class CommonConfigClient(object):
    def __init__(self, config_prefix):
        self.config_prefix = config_prefix

    def get_config(self, config_name):
        config_client = create_common_config_client(self.config_prefix, config_name)
        return config_client.get_root_json_value()
