from ext_cloud.BaseCloud.BaseServices.BaseService import BaseServicecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackServicecls(OpenStackBaseCloudcls, BaseServicecls):

    def __init__(self, **kwargs):
        self.__openstack_service = kwargs
        super(OpenStackServicecls, self).__init__(
            id=kwargs['id'], name=kwargs['name'])

    @property
    def state(self):
        return self.__openstack_service['state']

    @property
    def status(self):
        return self.__openstack_service['status']

    @property
    def port(self):
        return None

    @property
    def host(self):
        return self.__openstack_service['host']

    @property
    def group(self):
        return self.__openstack_service['group']
