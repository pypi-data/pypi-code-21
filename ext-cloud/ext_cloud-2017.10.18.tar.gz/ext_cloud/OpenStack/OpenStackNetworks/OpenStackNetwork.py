from ext_cloud.BaseCloud.BaseNetworks.BaseNetwork import BaseNetworkcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackSubnet import OpenStackSubnetcls


class OpenStackNetworkcls(OpenStackBaseCloudcls, BaseNetworkcls):

    def __init__(self, *arg, **kwargs):
        self.__openstack_network = arg[0]

        super(OpenStackNetworkcls, self).__init__(id=self.__openstack_network[
            'id'], name=self.__openstack_network['name'], credentials=kwargs['credentials'])

    @property
    def state(self):
        return self.__openstack_network['status']

    @property
    def is_external_network(self):
        return self.__openstack_network['router:external']

    @property
    def tenant_id(self):
        return self.__openstack_network['tenant_id']

    @property
    def is_zombie(self):
        if self.tenant_id is None or len(self.tenant_id) is 0:
            return True

        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        tenant = OpenStackIdentitycls(
            **self._credentials).get_tenant_by_id(self.tenant_id)
        if tenant is None:
            return True
        return False

    def list_subnets(self):
        return [OpenStackSubnetcls(openstack_subnet, credentials=self._credentials) for openstack_subnet in self._Clients.neutron.list_subnets(network_id=self.oid)['subnets']]

    def get_subnet_by_id(self, subnet_id):
        return [OpenStackSubnetcls(openstack_subnet, credentials=self._credentials) for openstack_subnet in self._Clients.neutron.list_subnets(id=subnet_id)['subnets']]

    def get_subnets_by_name(self, subnet_name):
        return [OpenStackSubnetcls(openstack_subnet, credentials=self._credentials) for openstack_subnet in self._Clients.neutron.list_subnets(name=subnet_name)['subnets']]

    def get_subnets_by_tag(self, tag_name, tag_value):
        pass

    def create_subnet(self, name=None, cidr_block=None, enable_dhcp=False, dns_nameservers=None):
        if dns_nameservers is None:
            dns_nameservers = ['8.8.8.8']
        if cidr_block is None:
            cidr_block = '10.0.0.0/24'
        params = {
            'subnet': {
                'network_id': self.oid,
                'ip_version': 4,
                'enable_dhcp': enable_dhcp,
                'dns_nameservers': dns_nameservers,
                'name': name,
                'cidr': cidr_block}}
        subnet_dict = self._Clients.neutron.create_subnet(params)
        openstack_subnet = subnet_dict['subnet']
        subnet = OpenStackSubnetcls(
            openstack_subnet, credentials=self._credentials)
        return subnet
