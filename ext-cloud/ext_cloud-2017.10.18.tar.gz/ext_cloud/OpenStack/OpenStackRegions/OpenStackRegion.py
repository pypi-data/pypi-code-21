from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.BaseCloud.BaseRegions.BaseRegion import BaseRegioncls


class OpenStackRegioncls(OpenStackBaseCloudcls, BaseRegioncls):

    def __init__(self, *args, **kwargs):
        super(OpenStackRegioncls, self).__init__(id=args[0], name=args[0], credentials=kwargs['credentials'])

    def list_zones(self):
        zones = self._Clients.nova.availability_zones.list()
        openstack_zones = []
        for zone in zones:
            from ext_cloud.OpenStack.OpenStackRegions.OpenStackZone import OpenStackZonecls
            zone = OpenStackZonecls(zone, credentials=self._credentials)
            openstack_zones.append(zone)
        return openstack_zones
