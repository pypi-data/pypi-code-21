from ext_cloud.BaseCloud.BaseNetworks.BaseNetworks import BaseNetworkscls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNetwork import OpenStackNetworkcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackSubnet import OpenStackSubnetcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNIC import OpenStackNICcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackFloatingIp import OpenStackFloatingIpcls
from ext_cloud.OpenStack.OpenStackNetworks.OpenStackRouter import OpenStackRoutercls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


from ext_cloud.utils.dogpile_utils import get_region
from dogpile.cache.api import NO_VALUE


class OpenStackNetworkscls(OpenStackBaseCloudcls, BaseNetworkscls):

    def __init__(self, **kwargs):
        super(OpenStackNetworkscls, self).__init__(credentials=kwargs)

    @property
    def Childrens(self):
        return self.list_networks() + self.list_routers() + self.list_nics() + self.list_floating_ips() + self.list_subnets()

    def list_metrics(self):
        metrics = []
        from ext_cloud.BaseCloud.BaseResources.BaseMetrics import BaseMetricscls
        metrics.append(BaseMetricscls('openstack.networks.count', len(self.list_networks())))
        metrics.append(BaseMetricscls('openstack.networks.subnets.count', len(self.list_subnets())))
        total = self.total_floating_ips
        all_fips = self.list_floating_ips()
        used = unused = 0
        for fip in all_fips:
            if fip.state == 'down':
                unused += 1
            else:
                used += 1
        free = total - len(all_fips)
        metrics.append(BaseMetricscls('openstack.networks.free_floating_ips', free))
        metrics.append(BaseMetricscls('openstack.networks.used_floating_ips', used))
        metrics.append(BaseMetricscls('openstack.networks.unallocated_floating_ips', unused))
        metrics.append(BaseMetricscls('openstack.networks.total_floating_ips', total))
        return metrics

    def get_network_by_id(self, network_id):
        return [OpenStackNetworkcls(openstack_network, credentials=self._credentials) for openstack_network in self._Clients.neutron.list_networks(id=network_id)['networks']]

    def get_networks_by_name(self, network_name):
        return [OpenStackNetworkcls(openstack_network, credentials=self._credentials) for openstack_network in self._Clients.neutron.list_networks(name=network_name)['networks']]

    def get_networks_by_tenant_id(self, tenant_id):
        return [OpenStackNetworkcls(openstack_network, credentials=self._credentials) for openstack_network in self._Clients.neutron.list_networks(tenant_id=tenant_id)['networks']]

    def get_networks_by_tag(self, tag_name, tag_value):
        pass

    def list_networks(self):
        return [OpenStackNetworkcls(openstack_network, credentials=self._credentials) for openstack_network in self._Clients.neutron.list_networks()['networks']]

    def list_external_networks(self):
        return [network for network in self.list_networks() if network.is_external_network]

    def list_external_networks_cache(self):
        region = get_region()
        # check if external networks is in cache
        networks = region.get('externalnetworks')

        if networks is NO_VALUE:
            dic = {}
            new_networks = self.list_external_networks()
            for network in new_networks:
                dic[network.id] = network.obj_to_dict()

            region.set('externalnetworks', dic)
            networks = dic

        return networks

    def create_network(self, name=None, cidr_block=None):
        params = {'network': {'name': name}}
        openstack_network_dic = self._Clients.neutron.create_network(params)
        openstack_network = openstack_network_dic['network']
        network = OpenStackNetworkcls(
            openstack_network, credentials=self._credentials)
        return network
    # ----------------- Subnet operations ------------------------- #

    def list_subnets(self):
        return [OpenStackSubnetcls(openstack_subnet, credentials=self._credentials) for openstack_subnet in self._Clients.neutron.list_subnets()['subnets']]

    def get_subnets_by_tenant_id(self, tenant_id):
        return [OpenStackSubnetcls(openstack_subnet, credentials=self._credentials) for openstack_subnet in self._Clients.neutron.list_subnets(tenant_id=tenant_id)['subnets']]

    def list_external_subnets(self):
        return [subnet for network in self.list_external_networks() for subnet in network.list_subnets()]

    def get_subnet_by_id(self, subnet_id):
        subnets = self.list_subnets()
        for subnet in subnets:
            if subnet.id == subnet_id:
                return subnet
        return None

    def get_subnets_by_name(self, subnet_name):
        pass

    def get_subnets_by_tag(self, tag_name, tag_value):
        pass

    # ----------------- Nic operations ------------------------- #
    def list_nics(self):
        return [OpenStackNICcls(openstack_nic, credentials=self._credentials) for openstack_nic in self._Clients.neutron.list_ports()['ports']]

    # ----------------- Router operations ------------------------- #
    def list_routers(self):
        return [OpenStackRoutercls(router, credentials=self._credentials) for router in self._Clients.neutron.list_routers()['routers']]

    def list_routers_from_cache(self):
        region = get_region()
        # check if routers is in cache
        routers = region.get('routers')

        if routers is NO_VALUE:
                # cache not created for routers, create a cache of all routers
            dic = {}
            new_routers = self.list_routers()
            for router in new_routers:
                dic[router.id] = router.obj_to_dict()

            region.set('routers', dic)
            routers = dic

        return routers

    def create_router(self, name=None):
        params = {'router': {'name': name}}
        openstack_router = self._Clients.neutron.create_router(params)
        router = OpenStackRoutercls(openstack_router['router'], credentials=self._credentials)
        return router

    # ----------------- Floating ip operations ------------------------- #
    def list_floating_ips(self):
        return [OpenStackFloatingIpcls(openstack_floating_ip, credentials=self._credentials) for openstack_floating_ip in self._Clients.neutron.list_floatingips()['floatingips']]

    def list_floating_ips_by_tenant_id(self, tenant_id):
        return [OpenStackFloatingIpcls(openstack_floating_ip, credentials=self._credentials) for openstack_floating_ip in self._Clients.neutron.list_floatingips(tenant_id=tenant_id)['floatingips']]

    def get_floating_ip_by_id(self, floatingip_id):
        openstack_floating_ip = self._Clients.neutron.show_floatingip(floatingip_id)
        return OpenStackFloatingIpcls(openstack_floating_ip['floatingip'], credentials=self._credentials)

    @property
    def total_floating_ips(self):
        return sum([subnet.count_total_ips for subnet in self.list_external_subnets()])

    @property
    def used_floating_ips(self):
        return sum([1 for floating_ip in self.list_floating_ips() if floating_ip.state == 'up'])

    @property
    def unallocated_floating_ips(self):
        return sum([1 for floating_ip in self.list_floating_ips() if floating_ip.state == 'down'])

    @property
    def free_floating_ips(self):
        return self.total_floating_ips - len(self.list_floating_ips())
