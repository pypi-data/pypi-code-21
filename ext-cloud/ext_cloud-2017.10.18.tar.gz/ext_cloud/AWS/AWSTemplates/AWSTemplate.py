from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.AWS.AWSCompute.AWSInstance import AWSInstancecls
from ext_cloud.BaseCloud.BaseTemplates.BaseTemplate import BaseTemplatecls
from boto.cloudformation.connection import CloudFormationConnection
from boto import ec2


class AWSTemplatecls(AWSBaseCloudcls, BaseTemplatecls):

    def __init__(self, *args, **kwargs):
        self.__cloudformation = None
        self.__ec2 = None
        data = args[0]

        super(AWSTemplatecls, self).__init__(id=data['id'], name=data['name'], credentials=kwargs['credentials'])

    @property
    def __CloudFormation(self):
        return self.__cloudformation

    @__CloudFormation.getter
    def __CloudFormation(self):
        if self.__cloudformation is None:
            self.__cloudformation = CloudFormationConnection(aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__cloudformation

    @property
    def __EC2(self):
        return self.__ec2

    @__EC2.getter
    def __EC2(self):
        if self.__ec2 is None:
            self.__ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__ec2

    def state(self):
        pass

    def validate_template(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def get_instances(self):
        results = self.__CloudFormation.describe_stack_resources(
            stack_name_or_id=self.name)
        instances = []
        for result in results:
            if result.resource_type != 'AWS::EC2::Instance':
                continue
            fetched_instances = self.__EC2.get_only_instances(instance_ids=result.physical_resource_id)
            if len(fetched_instances) < 1:
                continue
            fetched_instance = fetched_instances[0]
            instance = AWSInstancecls(fetched_instance, credentials=self._credentials)
            instances.append(instance)
        return instances
