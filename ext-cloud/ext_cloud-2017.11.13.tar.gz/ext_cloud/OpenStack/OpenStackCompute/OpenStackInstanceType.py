from ext_cloud.BaseCloud.BaseCompute.BaseInstanceType import BaseInstanceTypecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackInstanceTypecls(OpenStackBaseCloudcls, BaseInstanceTypecls):

    __openstack_instancetype = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_instancetype = arg[0]

        super(OpenStackInstanceTypecls, self).__init__(id=self.__openstack_instancetype.id,
                                                       name=self.__openstack_instancetype.name, credentials=kwargs['credentials'])

    @property
    def memory(self):
        return self.__openstack_instancetype.ram

    @property
    def disk(self):
        return self.__openstack_instancetype.disk

    @property
    def cpus(self):
        return self.__openstack_instancetype.vcpus
