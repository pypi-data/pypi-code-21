from ext_cloud.BaseCloud.BaseNetworks.BaseGateway import BaseGatewaycls
from boto import vpc
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSGatewaycls(AWSBaseCloudcls, BaseGatewaycls):

    __aws_gateway = None
    __vpc = None

    def __init__(self, *arg, **kwargs):
        self.__aws_gateway = arg[0]
        self._aws_ref = arg[0]
        name = None
        if 'name' in self.__aws_gateway.tags:
            name = self.__aws_gateway.tags['name']

        super(AWSGatewaycls, self).__init__(id=self.__aws_gateway.id, name=name, credentials=kwargs['credentials'])

    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.addtag('Name', value)
        self._name = value

    @property
    def state(self):
        return self.__aws_gateway.state

    @property
    def __Vpc(self):
        return self.__vpc

    @__Vpc.getter
    def __Vpc(self):
        if self.__vpc is None:
            self.__vpc = vpc.boto.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__vpc

    def delete(self):
        self.__Vpc.delete_internet_gateway(self._id)
