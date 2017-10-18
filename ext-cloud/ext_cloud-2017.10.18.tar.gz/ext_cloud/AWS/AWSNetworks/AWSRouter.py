from ext_cloud.BaseCloud.BaseNetworks.BaseRouter import BaseRoutercls
import boto.vpc
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSRoutercls(AWSBaseCloudcls, BaseRoutercls):

    __aws_router = None
    __vpc = None

    def __init__(self, *arg, **kwargs):
        self.__aws_router = arg[0]
        self._aws_ref = arg[0]
        name = None
        if 'name' in self.__aws_router.tags:
            name = self.__aws_router.tags['name']

        super(AWSRoutercls, self).__init__(id=self.__aws_router.id, name=name, credentials=kwargs['credentials'])

    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.addtag('Name', value)
        self._name = value

    @property
    def state(self):
        return self.__aws_router.state

    @property
    def __Vpc(self):
        return self.__vpc

    @__Vpc.getter
    def __Vpc(self):
        if self.__vpc is None:
            self.__vpc = boto.vpc.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__vpc

    def delete(self):
        self.__aws_router.delete()

    def add_route(self, destination_cidr_block=None, gateway_id=None, instance_id=None, interface_id=None):
        self.__Vpc.create_route(self._id, destination_cidr_block=destination_cidr_block, gateway_id=gateway_id, instance_id=instance_id, interface_id=interface_id)
