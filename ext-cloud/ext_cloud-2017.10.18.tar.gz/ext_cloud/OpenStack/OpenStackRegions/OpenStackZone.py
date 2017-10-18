from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.BaseCloud.BaseRegions.BaseZone import BaseZonecls


class OpenStackZonecls(OpenStackBaseCloudcls, BaseZonecls):

    def __init__(self, *args, **kwargs):
        self.__openstack_zone = args[0]
        super(OpenStackZonecls, self).__init__(id=self.__openstack_zone.zoneName,
                                               name=self.__openstack_zone.zoneName, credentials=kwargs['credentials'])

    @property
    def hosts_count(self):
        if self.__openstack_zone.hosts is None:
            return 0
        return len(self.__openstack_zone.hosts)

    @property
    def state(self):
        return 'up' if self.__openstack_zone.zoneState['available'] is True else 'down'
