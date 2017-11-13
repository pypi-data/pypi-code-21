from ext_cloud.BaseCloud.BaseNetworks.BaseSubnet import BaseSubnetcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNIC import OpenStackNICcls


class OpenStackSubnetcls(OpenStackBaseCloudcls, BaseSubnetcls):

    def __init__(self, *arg, **kwargs):
        self.__openstack_subnet = arg[0]

        super(OpenStackSubnetcls, self).__init__(id=self.__openstack_subnet['id'], name=self.__openstack_subnet['name'], credentials=kwargs['credentials'])

    @property
    def state(self):
        pass

    @property
    def cidr_block(self):
        return self.__openstack_subnet['cidr']

    @property
    def network_id(self):
        return self.__openstack_subnet['network_id']

    @property
    def tenant_id(self):
        return self.__openstack_subnet['tenant_id']

    @property
    def zone(self):
        pass

    def attach_nic(self, name=None, ip_address=None):
        if ip_address is None:
            fixed_ips = [{'subnet_id': self.oid}]
        else:
            fixed_ips = [{'ip_address': ip_address, 'subnet_id': self.oid}]
        params = {'port': {
            'name': name,
            'network_id': self.network_id,
            'fixed_ips': fixed_ips
        }
        }

        nic_dict = self._Clients.neutron.create_port(params)
        openstack_nic = nic_dict['port']
        nic = OpenStackNICcls(openstack_nic, credentials=self._credentials)
        return nic

    @property
    def count_total_ips(self):
        import netaddr
        count = 0
        for alloc_pool in self.__openstack_subnet['allocation_pools']:
            net_range = netaddr.IPRange(alloc_pool['start'], alloc_pool['end'])
            count += net_range.size

        return count
