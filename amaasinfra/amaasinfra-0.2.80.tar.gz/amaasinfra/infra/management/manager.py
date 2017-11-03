import boto3
import json


class CloudManager(object):
    """
    This class is an abstract class for managing cloud infra
    """
    def __init__(self):
        pass

    def list_all_instance(self):
        """
        Abstract method to be implemented by derived classes
        """
        raise NotImplementedError()


class AWSManager(CloudManager):
    """
    This is a simple infra manager for AWS
    """
    def __init__(self):
       pass

    def list_all_api_gateways(self):
        client = boto3.client('apigateway')


