from ext_cloud.BaseCloud.BaseNetworks.BaseNIC import BaseNICcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackNICcls(OpenStackBaseCloudcls, BaseNICcls):

    __openstack_nic = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_nic = arg[0]

        super(OpenStackNICcls, self).__init__(id=self.__openstack_nic['id'], name=self.__openstack_nic['name'], credentials=kwargs['credentials'])

    @property
    def state(self):
        return self.__openstack_nic['status']

    @property
    def mac_address(self):
        return self.__openstack_nic['mac_address']

    @property
    def network_id(self):
        return self.__openstack_nic['network_id']

    @property
    def tenant_id(self):
        return self.__openstack_nic['tenant_id']

    @property
    def is_zombie(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        tenant = OpenStackIdentitycls(**self._credentials).get_tenant_by_id(self.tenant_id)
        if tenant is None:
            return True
        return False

    @property
    def subnet_id(self):
        if 'fixed_ips' in self.__openstack_nic:
            return self.__openstack_nic['fixed_ips'][0]['subnet_id']
        return None

    @property
    def ip_address(self):
        if 'fixed_ips' in self.__openstack_nic:
            return self.__openstack_nic['fixed_ips'][0]['ip_address']
        return None

    @property
    def device_owner_type(self):
        owner = self.__openstack_nic['device_owner']
        if owner[0:7] == 'compute':
            return 'instance'
        elif owner == 'network:dhcp':
            return 'dhcp'
        elif owner == 'network:floatingip':
            return 'floatingip'
        elif owner == 'network:router_gateway':
            return 'router_gateway'
        elif owner == 'network:router_interface':
            return 'router_interface'
        else:
            return owner

    @property
    def device_owner_name(self):
        device_id = self.__openstack_nic['device_id']
        if self.device_owner_type == 'instance':
            from ext_cloud.OpenStack.OpenStackCompute.OpenStackCompute import OpenStackComputecls
            from novaclient.exceptions import NotFound
            try:
                instance = OpenStackComputecls(**self._credentials).get_instance_by_id_cache(device_id)
            except NotFound as _:
                return 'NA'
            return instance['name']
        elif self.device_owner_type == 'floatingip':
            return 'None'
        elif self.device_owner_type == 'dhcp':
            return 'None'
        elif self.device_owner_type == 'router_interface' or self.device_owner_type == 'router_gateway':
            from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNetworks import OpenStackNetworkscls
            routers = OpenStackNetworkscls(**self._credentials).list_routers_from_cache()
            if device_id in routers:
                return routers[device_id]['name']
            return 'NA'

        else:
            return 'TODO'

    @property
    def host_name(self):
        return self.__openstack_nic['binding:host_id']

    @property
    def is_external(self):
        if self.device_owner_type == 'floatingip':
            return True
        elif self.device_owner_type == 'dhcp':
            return False
        elif self.device_owner_type == 'router_interface':
            return False
        elif self.device_owner_type == 'router_gateway':
            return True
        elif self.device_owner_type == 'instance':
            return False

        return False

    @property
    def is_internal(self):
        return not self.is_external
