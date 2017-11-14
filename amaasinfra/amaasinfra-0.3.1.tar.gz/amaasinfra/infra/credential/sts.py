import boto3
from amaasinfra.infra.credential.policy import IoTPolicy

class STS(object):
    def __init__(self):
        self.client = boto3.client('sts')
    
    def assume_role(self):
        raise NotImplementedError()


class IoTSTS(STS):
    def __init__(self):
        super().__init__()

    def assume_role(self, role_arn, role_sesion_name, policy):
        return self.client.assume_role(RoleArn=role_arn,
                                       RoleSessionName=role_sesion_name,
                                       Policy=policy)



