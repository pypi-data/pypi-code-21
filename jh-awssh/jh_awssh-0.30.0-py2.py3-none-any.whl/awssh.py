# -*- coding: utf-8 -*-

import boto3
import os
import jmespath

""" Exceptions """

""" Boto client error """


class AwsClientErr(Exception):
    pass


""" Ec2 service error """


class Ec2Err(Exception):
    pass


class Ec2DescribeInstancesErr(Exception):
    pass


"""Main module."""


class Awssh(object):

    _clients = {}
    _default_region = 'us-west-2'
    _region = None

    def __init__(self, region=None):

        if region:
            self.set_region(region)
            # Awssh._region = region
        else:
            Awssh._region = Awssh.default_region()

    def client(self, service):

        client_key = '{0}-{1}'.format(service, Awssh.get_region())

        boto_kwargs = {}

        region_in = Awssh.get_region()

        if region_in and region_in is not None:
            boto_kwargs.update({'region_name': region_in})

        if not Awssh._clients.get(client_key):

            try:
                client = boto3.client(service, **boto_kwargs) or False  # noqa
            except Exception as e:  # noqa
                raise AwsClientErr("Unable to connect to AWS API: {0}".format(service))  # noqa

            if not client:
                raise AwsClientErr(
                    'Could not create service: {0}'.format(service))

            Awssh._clients.update({client_key: client})

        return Awssh._clients.get(client_key)

    @staticmethod
    def default_region():

        if os.environ.get("AWS_DEFAULT_REGION") is not None:
            return os.environ.get("AWS_DEFAULT_REGION")
        # return None
        return Awssh._default_region

    @staticmethod
    def get_region():
        return Awssh._region

    def set_region(self, region):
        try:
            regions = self.alias_regions()
        except Exception as e:  # noqa
            Awssh._region = region
            return

        if regions[0].get(region):
            region = regions[0].get(region)

        if region in regions[1]:
            new_region = region
        else:
            new_region = Awssh.default_region()

        Awssh._region = new_region

    def alias_regions(self):
        ec2 = self.client("ec2")
        r = ec2.describe_regions()
        region_names = jmespath.search("Regions[].RegionName", r)
        regions = []
        aliases = {}

        for r in region_names:
            spl = r.split('-')
            key = '{0}{1}{2}'.format(spl[0][:1], spl[1][:1], spl[2][:1])
            aliases.update({key: r})
            regions.append(r)

        return aliases, regions

    def return_ec2_servers(self, **kwargs):

        ec2Client = self.client('ec2')
        ipPath = 'PublicIpAddress'

        if kwargs.get('privateip'):
            ipPath = 'PrivateIpAddress'

        try:
            inst = ec2Client.describe_instances()
        except:  # noqa
            raise Ec2DescribeInstancesErr("Unable to connect to api")

        ips = []

        # compile JMESpath queries
        jmespath.compile("Tags[?Key=='Name'].Value")
        jmespath.compile("PublicIpAddress")
        jmespath.compile("PrivateIpAddress")

        for i in inst['Reservations']:
            for ii in i['Instances']:
                if ii['State']['Code'] not in [16]:
                    continue

                try:
                    name = jmespath.search("Tags[?Key=='Name'].Value", ii)[0]
                except:  # noqa
                    name = 'N/A'

                try:
                    ip = jmespath.search(ipPath, ii)
                except:  # noqa
                    ip = False

                if ip:
                    ips.append({'Name': name, 'Ip': ip})

        return ips

    def return_elastic_ips(self, **kwargs):

        ec2Client = self.client('ec2')

        ips = []
        try:
            eips = ec2Client.describe_addresses()
        except:  # noqa
            exit("Unable to connect to AWS API")

        for ip in eips['Addresses']:
            if 'PublicIp' in ip:
                ips.append(ip['PublicIp'])

        return ips

    def return_server_list(self, **kwargs):

        servers = self.return_ec2_servers(**kwargs)
        eips = self.return_elastic_ips()

        for k, v in enumerate(servers):
            tag = ' '
            if v['Ip'] in eips:
                tag = '✓'
            # pad the ips for uniformity
            while len(servers[k]['Ip']) < 15:
                servers[k]['Ip'] = ' {0}'.format(v['Ip'])
            servers[k].update({'Eip': tag})

        def cmp(x, y):
            if x['Name'] < y['Name']:
                return -1
            return 0

        servers = sorted(servers, cmp=cmp)

        return servers

    def list_ips(self, name, **kwargs):

        exact = False

        if kwargs.get('exact'):
            exact = kwargs['exact']

        servers = self.return_ec2_servers(**kwargs)

        ips = []

        if len(servers) <= 0:
            return ips

        name = name.lower()

        for k, v in enumerate(servers):
            if len(name) > 0:
                if exact:
                    if name == v['Name'].lower():
                        ips.append(v['Ip'])
                else:
                    if name in v['Name'].lower():
                        ips.append(v['Ip'])
            else:
                ips.append(v['Ip'])

        return ips
