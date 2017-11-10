import boto3

ssm_max_results = 50


class Ssm(object):

    def __init__(self, profile, region):
        self.session = boto3.session.Session(
            profile_name=profile, region_name=region)
        self.region = region
        self.client = self.session.client('ssm')
        self.InstanceIds = []

    def get_document(self, name, version=None):
        params = {'Name': name}
        if version:
            params['DocumentVersion'] = version
        response = self.client.get_document(**params)
        return response

    def list_documents(self):
        """ Return a list of SSM Docutments """
        response = self.client.list_documents(MaxResults=ssm_max_results)
        docs = response['DocumentIdentifiers']
        while True:
            if 'NextToken' not in response:
                break
            response = self.client.list_documents(
                NextToken=response['NextToken'], MaxResults=ssm_max_results)
            docs += response['DocumentIdentifiers']
        return docs

    def send_command_to_targets(self, document, key, value, comment, parameters):
        """ Send command to key/value taget """
        response = self.client.send_command(
            Targets=[
                {
                    'Key': 'tag:' + key,
                    'Values': [value]
                },
            ],
            DocumentName=document,
            Parameters=parameters,
            Comment=comment
        )
        return response['Command']

    def list_commands(self, CommandId=None, InstanceId=None):
        params = {
            'MaxResults': ssm_max_results
        }
        if CommandId:
            params['CommandId'] = CommandId
        if InstanceId:
            params['InstanceId'] = InstanceId

        response = self.client.list_commands(**params)
        commands = response['Commands']
        while True:
            if 'NextToken' not in response:
                break
            params['NextToken'] = response['NextToken']
            response = self.client.list_commands(**params)
        commands += response['Commands']
        return commands

    def list_command_invocations(self, CommandId=None, InstanceId=None, Details=False):
        params = {
            'MaxResults': ssm_max_results,
            'Details': Details
        }
        if CommandId:
            params['CommandId'] = CommandId
        if InstanceId:
            params['InstanceId'] = InstanceId

        response = self.client.list_command_invocations(**params)
        invocations = response['CommandInvocations']
        while True:
            if 'NextToken' not in response:
                break
            params['NextToken'] = response['NextToken']
            response = self.client.list_command_invocations(**params)
            invocations += response['CommandInvocations']
        return invocations

    def command_url(self, CommandId):
        if self.region is None:
            self.region = 'us-east-1'
        return 'https://console.aws.amazon.com/ec2/v2/home?region=' + \
            self.region + '#Commands:CommandId=' + \
            str(CommandId) + ';sort=CommandId'
