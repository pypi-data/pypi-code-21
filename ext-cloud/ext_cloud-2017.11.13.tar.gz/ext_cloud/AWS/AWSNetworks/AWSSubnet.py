from ext_cloud.BaseCloud.BaseNetworks.BaseSubnet import BaseSubnetcls
import boto.vpc
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSSubnetcls(AWSBaseCloudcls, BaseSubnetcls):

    __aws_subnet = None
    __vpc = None

    def __init__(self, *arg, **kwargs):
        self.__aws_subnet = arg[0]
        self._aws_ref = arg[0]
        name = None
        if 'name' in self.__aws_subnet.tags:
            name = self.__aws_subnet.tags['name']

        super(AWSSubnetcls, self).__init__(id=self.__aws_subnet.id, name=name, credentials=kwargs['credentials'])

    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.addtag('Name', value)
        self._name = value

    @property
    def __Vpc(self):
        return self.__vpc

    @__Vpc.getter
    def __Vpc(self):
        if self.__vpc is None:
            self.__vpc = boto.vpc.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__vpc

    @property
    def state(self):
        return self.__aws_subnet.state

    @property
    def cidr_block(self):
        return self.__aws_subnet.cidr_block

    @property
    def network_id(self):
        return self.__aws_subnet.vpc_id

    @property
    def zone(self):
        return self.__aws_subnet.availability_zone

    def delete(self):
        self.__Vpc.delete_subnet(self._id)

    def attach_router(self, router_id=None):
        self.__Vpc.associate_route_table(router_id, self._id)
        return True

    def detach_router(self, router_id=None):
        pass
