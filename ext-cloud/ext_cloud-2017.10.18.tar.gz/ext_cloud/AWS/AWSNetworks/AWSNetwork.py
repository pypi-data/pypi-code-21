from ext_cloud.BaseCloud.BaseNetworks.BaseNetwork import BaseNetworkcls
import boto.vpc
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.AWS.AWSNetworks.AWSSubnet import AWSSubnetcls
from ext_cloud.AWS.AWSNetworks.AWSRouter import AWSRoutercls
from ext_cloud.AWS.AWSNetworks.AWSGateway import AWSGatewaycls


class AWSNetworkcls(AWSBaseCloudcls, BaseNetworkcls):

    def __init__(self, *arg, **kwargs):
        self.__vpc = None
        self.__aws_network = arg[0]
        self._aws_ref = arg[0]
        name = None
        if 'name' in self.__aws_network.tags:
            name = self.__aws_network.tags['name']

        super(AWSNetworkcls, self).__init__(id=self.__aws_network.id, name=name, credentials=kwargs['credentials'])

    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.addtag('Name', value)
        self._name = value

    @property
    def state(self):
        return self.__aws_network.state

    @property
    def __Vpc(self):
        return self.__vpc

    @__Vpc.getter
    def __Vpc(self):
        if self.__vpc is None:
            self.__vpc = boto.vpc.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__vpc

    def delete(self):
        self.__aws_network.delete()

    def list_subnets(self):
        filters = dict()
        filters['vpc-id'] = self._id
        aws_subnets = self.__Vpc.get_all_subnets(filters=filters)
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

        aws_dict = {}
        aws_dict['vpc-id'] = self.oid
        if 'cidr_block' in filter_dict:
            aws_dict['cidrBlock'] = filter_dict['cidr_block']
        subnets = []
        aws_subnets = self.__Vpc.get_all_subnets(filters=aws_dict)
        for aws_subnet in aws_subnets:
            subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
            subnets.append(subnet)

        return subnets

    def create_subnet(self, name=None, cidr_block=None, zone=None):
        aws_subnet = self.__Vpc.create_subnet(
            self._id, cidr_block, availability_zone=zone)
        subnet = AWSSubnetcls(aws_subnet, credentials=self._credentials)
        if name is not None:
            subnet.name = name

        # auto assign public ip for subnet
        orig_api_version = self.__Vpc.APIVersion
        self.__Vpc.APIVersion = '2014-06-15'
        self.__Vpc.get_status(
            'ModifySubnetAttribute',
            {'SubnetId': aws_subnet.id, 'MapPublicIpOnLaunch.Value': 'true'},
            verb='POST')
        self.__Vpc.APIVersion = orig_api_version

        # assign router to subnet for public access
        from ext_cloud.AWS.AWSNetworks.AWSNetworks import AWSNetworkscls
        network_connection = AWSNetworkscls(**self._credentials)
        network = network_connection.get_network_by_id(subnet.network_id)
        routers = network.get_all_routers()
        router = routers[0]
        subnet.attach_router(router.id)
        gateway = network.get_gateway()
        router.add_route(destination_cidr_block='0.0.0.0/0', gateway_id=gateway.id)

        return subnet

    def attach_gateway(self, gateway_id):
        self.__Vpc.attach_internet_gateway(gateway_id, self._id)
        return True

    def detach_gateway(self, gateway_id):
        self.__Vpc.detach_internet_gateway(gateway_id, self._id)
        return True

    def get_gateway(self):
        filters = dict()
        filters['attachment.vpc-id'] = self._id
        result_set = self.__Vpc.get_all_internet_gateways(filters=filters)
        if len(result_set) < 1:
            return None
        aws_gateway = result_set.pop()
        gateway = AWSGatewaycls(aws_gateway, credentials=self._credentials)
        return gateway

    def get_all_routers(self):
        filters = dict()
        filters['vpc-id'] = self._id
        aws_routers = self.__Vpc.get_all_route_tables(filters=filters)
        routers = []
        for aws_router in aws_routers:
            router = AWSRoutercls(aws_router, credentials=self._credentials)
            routers.append(router)

        return routers
