""" Logs calls to the AMaaS APIs """

from datetime import datetime

import boto3

class APICallLogger(object):
    """ The current implementation of the API Call Logger uses Cloudwatch metrics """

    def __init__(self):
        self.client = None

    def record_api_call(self, asset_manager_id, api_call_type, api_call_subtype,
                        client_id=None, token_asset_manager_id=None,
                        username=None, environment='dev'):
        """ Record the API call """
        if not self.client:
            self.client = boto3.client('cloudwatch')

        asset_manager_id = str(asset_manager_id)  # In case it gets sent in as an integer
        dimensions = [{'Name': 'api_call_type', 'Value': api_call_type},
                      {'Name': 'api_call_subtype', 'Value': api_call_subtype},
                      {'Name': 'asset_manager_id', 'Value': str(asset_manager_id)},
                      {'Name': 'environment', 'Value': environment}]

        if client_id:
            dimensions.append({'Name': 'client_id', 'Value': str(client_id)})

        if token_asset_manager_id:
            dimensions.append({'Name': 'token_asset_manager_id',
                               'Value': str(token_asset_manager_id)})

        if username:
            dimensions.append({'Name': 'username', 'Value': username})

        self.client.put_metric_data(
            Namespace='amaas',
            MetricData=[
                {
                    'MetricName': 'AMaaSAPICalls',
                    'Dimensions': dimensions,
                    'Timestamp': datetime.utcnow(),
                    'Value': 1.0,
                    'Unit': 'Count'
                },
            ]
        )
