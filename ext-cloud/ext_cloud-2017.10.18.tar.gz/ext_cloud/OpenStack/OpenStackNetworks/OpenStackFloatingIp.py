from ext_cloud.BaseCloud.BaseNetworks.BaseFloatingIp import BaseFloatingIpcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackFloatingIpcls(OpenStackBaseCloudcls, BaseFloatingIpcls):

    __openstack_floating_ip = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_floating_ip = arg[0]

        super(OpenStackFloatingIpcls, self).__init__(id=self.__openstack_floating_ip[
            'id'], name=self.__openstack_floating_ip['floating_ip_address'], credentials=kwargs['credentials'])

    @property
    def state(self):
        if self.__openstack_floating_ip['status'] == 'ACTIVE':
            return 'up'
        elif self.__openstack_floating_ip['status'] == 'DOWN':
            return 'down'
        else:
            return 'na'

    @property
    def floating_ip_address(self):
        return self.__openstack_floating_ip['floating_ip_address']

    @property
    def fixed_ip_address(self):
        return self.__openstack_floating_ip['fixed_ip_address']

    @property
    def tenant_id(self):
        return self.__openstack_floating_ip['tenant_id']

    @property
    def tenant_name(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        identity = OpenStackIdentitycls(**self._credentials)
        tenants = identity.list_tenants_cache()
        return tenants[self.tenant_id]['name'] if self.tenant_id in tenants else None

    @property
    def nic_id(self):
        return self.__openstack_floating_ip['port_id']

    @property
    def network_id(self):
        return self.__openstack_floating_ip['floating_network_id']

    @property
    def subnet_id(self):
        pass
