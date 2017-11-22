#!/usr/bin/env python
import sys
import os
import boto3
import time
import vmtools
from awsretry import AWSRetry
import botohelper.route53 as route53
import botohelper.botohelpermain

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Ec2(botohelper.botohelpermain.Main):
    """Class to manipulate aws ec2 resources

    public methods:
    delete_vpc
    delete_instances 
    create_vpc
    create_subnet
    create_internet_gateway
    get_object_from_name
    get_environment_from_vpc_name
    get_default_route_table_object
    get_default_security_group_object 
    create_tag
    create_instance
    get_latest_ami_from_prefix

    instance variables:
    self.aws_profile
    self.aws_region
    self.session
    self.client_ec2
    self.ec2
    self.availability_zones_list
    self.route53
    """

    def __init__(self, aws_profile, aws_region):
        """set instance variables, set instance aws connections

        keyword arguments:
        :type aws_profile: string
        :param aws_profile: the profile to use from ~/.aws/credentials to connect to aws
        :type aws_region: string
        :param aws_region: the region to use for the aws connection object (all resources will be created in this region)
        """
        super().__init__(aws_profile=aws_profile, aws_region=aws_region)
        self.route53 = route53.Route53(aws_profile=self.aws_profile, aws_region=self.aws_region)

    def delete_vpc(self, vpc_name):
        """Create a vpc return vpc_id
        keyword arguments:
        :type vpc_name: string
        :param vpc_name: the Name tag for the vpc
        :type cidr_block: string
        :param cidr_block: cidr_block for the new vpc (ex '10.0.1.0/24')
        :type environment: string
        :param environment: the enviroment tag for the vpc
        """
        vpc_object = self.get_object_from_name(tag_name=vpc_name, object_type='vpc', fail_condition='doesnt_exist')
        self.delete_instances(instance_object_list=list(vpc_object.instances.all()))
        for sec_group in list(vpc_object.security_groups.all()):
            if sec_group.group_name != 'default':
                sec_group.delete()
        for subnet in list(vpc_object.subnets.all()):
            subnet.delete()
        for internet_gateway in list(vpc_object.internet_gateways.all()):
            internet_gateway.detach_from_vpc(VpcId=vpc_object.vpc_id)
            time.sleep(3)
            internet_gateway.delete()
        time.sleep(3)
        vpc_object.delete()

    def delete_instances(self, instance_object_list):
        """Take list of instance objects and delete all instances and associated stuff
        keyword arguments:
        :type instance_object_list: list
        :param instance_object_list: a list of instance objects (ex instance_object = ec2.Instance('<instance_id>'))
        """
        instance_id_list = [ instance_object.instance_id for instance_object in instance_object_list ]
        # walk through and delete all instances
        for instance_object in instance_object_list:
            # if we have a hostname delete dns entries
            if instance_object.tags:
                for tag_dict in instance_object.tags:
                    if tag_dict['Key'] == 'Name':
                        hostname = tag_dict['Value']
                # get the public dns record for instance
                public_dns_record = self.route53.get_route53_record(fqdn=hostname, record_type='A', zone_group_type='public_zones')
                # if public dns record exists delete it
                if public_dns_record:
                    self.route53.modify_a_record(fqdn=hostname, ip_address=public_dns_record['ResourceRecords'][0]['Value'], action='delete', ttl=public_dns_record['TTL'], zone_group_type='public_zones')
                # get the private dns record for instance
                private_dns_record = self.route53.get_route53_record(fqdn=hostname, record_type='A', zone_group_type='private_zones')
                # if private dns record exists delete it
                if private_dns_record:
                    self.route53.modify_a_record(fqdn=hostname, ip_address=private_dns_record['ResourceRecords'][0]['Value'], action='delete', ttl=private_dns_record['TTL'], zone_group_type='private_zones')
            instance_object.terminate()
        # wait for all instances to be terminated
        while instance_id_list:
            for instance_id in instance_id_list:
                instance_object = self.ec2.Instance(instance_id)
                if instance_object.state['Name'] == 'terminated':
                    instance_id_list.remove(instance_id)
            print('''Waiting for instance(s) to terminate''', end='\r')
            time.sleep(5)

    def create_vpc(self, vpc_name, cidr_block, environment):
        """Create a vpc return vpc_id
        keyword arguments:
        :type vpc_name: string
        :param vpc_name: the Name tag for the vpc
        :type cidr_block: string
        :param cidr_block: cidr_block for the new vpc (ex '10.0.1.0/24')
        :type environment: string
        :param environment: the enviroment tag for the vpc
        """
        # check if a vpc with this name already exists (this will fail out if vpc exists already)
        vpc_object = self.get_object_from_name(tag_name=vpc_name, object_type='vpc', fail_condition='exists')
        # create the vpc
        response = self.client_ec2.create_vpc( CidrBlock = cidr_block)
        vpc_id = response['Vpc']['VpcId']
        # get the vpc object
        vpc_object = self.ec2.Vpc(vpc_id)
        # create Name tag
        self.create_tag(resource_object=vpc_object, tags_list_of_dict=[{'Key': 'Name', 'Value': vpc_name},])
        # create environment tag
        self.create_tag(resource_object=vpc_object, tags_list_of_dict=[{'Key': 'Environment', 'Value': environment},])
        # create internet gateway
        internet_gateway_name='{}_internet_gateway'.format(vpc_name)
        internet_gateway = self.create_internet_gateway(internet_gateway_name=internet_gateway_name)
        internet_gateway.attach_to_vpc(VpcId=vpc_id)
        # find default route table and name
        default_route_table_name = '{}_default_route_table'.format(vpc_name)
        default_route_table = self.get_default_route_table_object(vpc_object=vpc_object)
        self.create_tag(resource_object=default_route_table, tags_list_of_dict=[{'Key': 'Name', 'Value': default_route_table_name},])
        # find default security group and name
        default_security_group_name = '{}_default_security_group'.format(vpc_name)
        default_security_group = self.get_default_security_group_object(vpc_object=vpc_object)
        self.create_tag(resource_object=default_security_group, tags_list_of_dict=[{'Key': 'Name', 'Value': default_security_group_name},])
        # return dictionary with the new objects
        vpc_object_dict = {'vpc_object': vpc_object, 'internet_gateway': internet_gateway, 'default_route_table': default_route_table, 'default_security_group': default_security_group }
        return vpc_object_dict

    def create_subnet(self, vpc_object, subnet_name, cidr_block, availability_zone):
        """Create a subnet in vpc, return subnet object
        keyword arguments:
        :type vpc_object: boto3 vpc object (ex: <class 'boto3.resources.factory.ec2.Vpc'>)
        :param vpc_object: vpc object
        :type subnet_name: string
        :param subnet_name: name for the new subnet
        :type cidr_block: string
        :param cidr_block: cidr_block for the new subnet, must be within the vpc and not overlapping with another subnet (ex '10.0.1.0/24')
        :type availability_zone: string
        :param availability_zone: the availability_zone for the new subnet
        """
        subnet = vpc_object.create_subnet(CidrBlock=cidr_block, AvailabilityZone=availability_zone)
        # create Name tag
        self.create_tag(resource_object=subnet, tags_list_of_dict=[{'Key': 'Name', 'Value': subnet_name},])
        return subnet

    def create_internet_gateway(self, internet_gateway_name):
        """Create an internet gateway return internet gateway object
        keyword arguments:
        :type internet_gateway_name: string
        :param internet_gateway_name: Name tag for the internet gateway
        """
        internet_gateway = self.ec2.create_internet_gateway()
        # create Name tag
        self.create_tag(resource_object=internet_gateway, tags_list_of_dict=[{'Key': 'Name', 'Value': internet_gateway_name},])
        return internet_gateway

    def get_object_from_name(self, tag_name, object_type, fail_condition=None):
        """Take tag_name and object_type then return aws_object or None depending on the fail_condition
        Note: this function will always fail if it finds more than one object with the same name tag
        keyword arguments:
        :type tag_name: string
        :param tag_name: the value of the Name tag for the aws_object
        :type object_type: string
        :param object_type: the type of object it is (ex instance, vpc, subnet etc)
        :type fail_condition: string
        :param fail_condition: the condition which will cause this function to error and exit the program. possible values are: exists (fail if the object exists), doesnt_exist (fail if the object doesn't exisit), or None (if the object exists, return object, if it doesn't return None)
        """
        # create object type for boto3 (object_types should end in 's') and messaging
        if object_type.endswith('s'):
            object_type_plural = object_type
            object_type_singular = object_type[:-1]
        else:
            object_type_plural = '{}s'.format(object_type)
            object_type_singular = object_type
        if object_type_plural == 'instances':
            # for instances we only want instances that are "up", ignore anything that is "down"
            filters = [{'Name':'tag:Name', 'Values':[tag_name]}, {'Name':'instance-state-name', 'Values':['running', 'pending', 'rebooting']}]
        else:
            filters = [{'Name':'tag:Name', 'Values':[tag_name]}]
        # filter all object of that type by our tag name and other stuff
        result = list(getattr(self.ec2, object_type_plural).filter(Filters=filters))
        if result:
            if len(result) == 1:
                aws_object = result[0]
                if fail_condition == 'exists':
                    fail_on_exists_message = 'Failure: A(n) {} with tag name "{}" already exists (object listed below). Botohelper requires "Name tags" to be unique. Quitting...\n{}'.format(object_type_singular, tag_name, result)
                    print(fail_on_exists_message)
                    sys.exit(1)
            else:
                too_many_objects_message = 'Failure: filtering {} by tag name "{}" resulted in more than one {} objects (listed below). Botohelper requires "Name tags" to be unique. Quitting...\n{}'.format(object_type_plural, tag_name, object_type_singular, result)
                print(too_many_objects_message)
                sys.exit(1)
        else:
            if fail_condition == 'doesnt_exist':
                fail_on_doesnt_exists_message = 'Failure: Could not find a {} with tag name "{}". Quitting...\n'.format(object_type_singular, tag_name)
                print(fail_on_doesnt_exists_message)
                sys.exit(1)
            aws_object = None
        return aws_object

    def get_environment_from_vpc_name(self, vpc_name):
        """Take vpc_name return vpc environment
        keyword arguments:
        :type vpc_name: string
        :param vpc_name: the tag Name for the vpc
        """
        # get vpc object
        vpc_object = self.get_object_from_name(tag_name=vpc_name, object_type='vpc', fail_condition='doesnt_exist')
        # step through tags and get Environment
        for tag_dict in vpc.tags:
            if tag_dict['Key'] == 'Environment':
                vpc_environment = tag_dict['Value']
        # make sure we have an environment
        if not vpc_environment:
            exception_message = 'Fail: the vpc: {} does not have an Environment tag. Correct this now.'.format(vpc_id)
            raise ValueError(exception_message)
        return vpc_environment


    def get_default_route_table_object(self, vpc_object):
        """Find default route table for vpc_object, return default route table object
        IMPORTANT: only run this before any other route tables have been create (it exprects there to be only one route table)
        keyword arguments:
        :type vpc_object: boto3 vpc object (ex: <class 'boto3.resources.factory.ec2.Vpc'>)
        :param vpc_object: vpc object
        """
        route_tables_collection = vpc_object.route_tables
        route_tables_list = list(route_tables_collection.all())
        # make sure we only have 1 route table in the list
        if len(route_tables_list) != 1:
            exception_message = 'Fail: the method "get_default_route_table_object" found: {} route tables for vpc: {}. Expecting only one'.format(len(route_tables_list), vpc_object.vpc_id) 
            raise ValueError(exception_message)
        return route_tables_list[0]

    def get_default_security_group_object(self, vpc_object):
        """Find default security group for vpc_object, return default security group object
        IMPORTANT: only run this before any other security groups have been create (it exprects there to be only one security group)
        keyword arguments:
        :type vpc_object: boto3 vpc object (ex: <class 'boto3.resources.factory.ec2.Vpc'>)
        :param vpc_object: vpc object
        """
        security_groups_collection = vpc_object.security_groups
        security_groups_list = list(security_groups_collection.all())
        # make sure we only have 1 route table in the list
        if len(security_groups_list) != 1:
            exception_message = 'Fail: the method "get_default_security_group_object" found: {} security groups for vpc: {}. Expecting only one'.format(len(security_groups_list), vpc_object.vpc_id) 
            raise ValueError(exception_message)
        return security_groups_list[0]

    @AWSRetry.backoff()
    def create_tag(self, resource_object, tags_list_of_dict):
        """Create tags for a resource
        keyword arguments:
        :type resource_object: boto3 resource object (ex: <class 'boto3.resources.factory.ec2.Vpc'>)
        :param resource_object: a object that represents an aws resource, one way to get it is filter a collection ex (ec2.vpcs.filter(VpcIds=[vpc_id]))
        :type tags_list_of_dict: list
        :param tags_list_of_dict: a list of dictionaries. One dict for each tag ex: [{'Key': 'Name', 'Value': 'vpctest'},]
        """
        resource_object.create_tags(Tags=tags_list_of_dict)

    def create_instance(self, instance_name, subnet_id, keypair_name, ami_id, instance_size='t2.medium', public_ip=False, instance_profile_arn=None):
        """Create instance, return instance object
        keyword arguments:
        :type instance_name: string
        :param instance_name:  the Name tag for the new instance
        :type subnet_id: string
        :param subnet_id:  the subnet in which to launch the instance
        :type keypair_name: string
        :param keypair_name: the name of the keypair to assign the new instance
        :type instance_size: string
        :param instance_size: the size of the instance
        :type public_ip: boolean
        :param public_ip: should instance have a public ip? True of False
        :type instance_profile_arn: string
        :param instance_profile_arn: (optional) the arn of the instance profile to use
        """
        # check if instance with this name tag exists already (will fail if one exists)
        instance_object = self.get_object_from_name(tag_name=instance_name, object_type='instance', fail_condition='exists')
        # launch instance
        if instance_profile_arn:
            instances_list = self.ec2.create_instances( ImageId=ami_id, MinCount=1, MaxCount=1, KeyName=keypair_name, InstanceType=instance_size, NetworkInterfaces=[ {'DeviceIndex': 0, 'SubnetId': subnet_id, 'AssociatePublicIpAddress': public_ip} ], IamInstanceProfile={ 'Arn': instance_profile_arn })
        else:
            instances_list = self.ec2.create_instances( ImageId=ami_id, MinCount=1, MaxCount=1, KeyName=keypair_name, InstanceType=instance_size, NetworkInterfaces=[ {'DeviceIndex': 0, 'SubnetId': subnet_id, 'AssociatePublicIpAddress': public_ip} ])
        instance_object = instances_list[0]
        # create Namte tag
        self.create_tag(resource_object=instance_object, tags_list_of_dict=[{'Key': 'Name', 'Value': instance_name},])
        return instance_object

    def get_latest_ami_from_prefix(self, ami_name_prefix):
        """Find the latest ami based on ami_name_prefix, return ami object
        keyword arguments:
        :type ami_name_prefix: string
        :param ami_name_prefix: the prefix to filter should end in asterix (ex: 'company-ubuntu-16.04-ami*')
        """
        # get all amis that match ami_name_prefix and put in a dict using the name tag as key
        ami_list = list( self.ec2.images.filter(Filters=[{'Name':'name', 'Values':[ami_name_prefix]}]).all())
        ami_dict = {ami.name: ami for ami in ami_list }
        # latest will have the highest number
        latest_ami_name = sorted(ami_list)[-1].name
        ami_object = ami_dict[latest_ami_name]
        return ami_object

