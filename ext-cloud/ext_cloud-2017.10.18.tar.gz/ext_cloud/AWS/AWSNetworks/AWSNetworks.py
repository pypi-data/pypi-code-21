from ext_cloud.BaseCloud.BaseNetworks.BaseNetworks import BaseNetworkscls
from ext_cloud.AWS.AWSNetworks.AWSNetwork import AWSNetworkcls
from ext_cloud.AWS.AWSNetworks.AWSSubnet import AWSSubnetcls
from ext_cloud.AWS.AWSNetworks.AWSGateway import AWSGatewaycls
import boto.vpc
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSNetworkscls(AWSBaseCloudcls, BaseNetworkscls):

    def __init__(self, **kwargs):
        self.__vpc = None
        self._credentials['username'] = kwargs['username']
        self._credentials['password'] = kwargs['password']
        self._credentials['region_name'] = kwargs['region_name']

    @property
    def __Vpc(self):
        return self.__vpc

    @__Vpc.getter
    def __Vpc(self):
        if self.__vpc is None:
            self.__vpc = boto.vpc.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__vpc

    def list_networks(self):
        aws_vpcs = self.__Vpc.get_all_vpcs()
        vpcs = []
        for aws_vpc in aws_vpcs:
            vpc = AWSNetworkcls(aws_vpc, credentials=self._credentials)
            vpcs.append(vpc)

        return vpcs

    def get_network_by_id(self, network_id):
        vpc_ids = []
        vpc_ids.append(network_id)
        result_set = self.__Vpc.get_all_vpcs(vpc_ids=vpc_ids)
        aws_vpc = result_set.pop()
        vpc = AWSNetworkcls(aws_vpc, credentials=self._credentials)
        return vpc

    def get_networks_by_name(self, network_name):
        pass

    def get_networks_by_tag(self, tag_name, tag_value):
        network_filters = {'tag-key': tag_name, 'tag-value': tag_value}
        networks = []
        aws_networks = self.__Vpc.get_all_vpcs(filters=network_filters)
        for aws_network in aws_networks:
            network = AWSNetworkcls(aws_network, credentials=self._credentials)
            networks.append(network)

        return networks

    def create_network(self, name=None, cidr_block=None):
        aws_network = self.__Vpc.create_vpc(cidr_block)
        vpc = AWSNetworkcls(aws_network, credentials=self._credentials)
        if name is not None:
            vpc.name = name
        # create gateway and attached to this network
        aws_gateway = self.create_gateway(name=vpc.name)
        vpc.attach_gateway(aws_gateway.id)

        return vpc

    def create_gateway(self, name=None):
        aws_gateway = self.__Vpc.create_internet_gateway()
        gateway = AWSGatewaycls(aws_gateway, credentials=self._credentials)
        if name is not None:
            gateway.name = name
        return gateway

    def list_subnets(self):
        aws_subnets = self.__Vpc.get_all_subnets()
        subnets = []
        for aws_subnet in aws_subnets:
            subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
            subnets.append(subnet)

        return subnets

    def get_subnet_by_id(self, subnet_id):
        subnet_ids = []
        subnet_ids.append(subnet_id)
        result_set = self.__Vpc.get_all_subnets(subnet_ids=subnet_ids)
        aws_subnet = result_set.pop()
        subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
        return subnet

    def get_subnets_by_name(self, subnet_name):
        pass

    def get_subnets_by_tag(self, tag_name, tag_value):
        subnet_filters = {'tag-key': tag_name, 'tag-value': tag_value}
        subnets = []
        aws_subnets = self.__Vpc.get_all_subnets(filters=subnet_filters)
        for aws_subnet in aws_subnets:
            subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
            subnets.append(subnet)

        return subnets

    def get_subnets_by_filter(self, filter_dict):

        aws_dict = dict()
        if 'cidr_block' in filter_dict:
            aws_dict['cidrBlock'] = filter_dict['cidr_block']
        subnets = []
        aws_subnets = self.__Vpc.get_all_subnets(filters=aws_dict)
        for aws_subnet in aws_subnets:
            subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
            subnets.append(subnet)

        return subnets
