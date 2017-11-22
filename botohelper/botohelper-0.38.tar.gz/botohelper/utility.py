#!/usr/bin/env python
import sys
import os
import boto3
import time
import re
import vmtools
import botohelper.botohelpermain

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Utility(botohelper.botohelpermain.Main):
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

    def build_collection_method_from_camel_method(self, camel_case_method):
        # exceptions_dict format: if collection_method_singular ends with 'key' add on the 'value' else add an 's'
        exceptions_dict = {
                'ss': 'es',
                'options': '_sets'
                }
        collection_method_singular = re.sub( '(?<!^)(?=[A-Z])', '_', camel_case_method ).lower()
        for ending in exceptions_dict:
            if collection_method_singular.endswith(ending):
                collection_method_plural = '{}{}'.format(collection_method_singular, exceptions_dict[ending])
                return collection_method_plural
        collection_method_plural = '{}s'.format(collection_method_singular)
        return collection_method_plural

    def build_resource_dict(self):
        """Create a vpc return vpc_id
        keyword arguments:
        :type vpc_name: string
        :param vpc_name: the Name tag for the vpc
        :type cidr_block: string
        :param cidr_block: cidr_block for the new vpc (ex '10.0.1.0/24')
        :type environment: string
        :param environment: the enviroment tag for the vpc
        """
        known_missiong_collection_methods_list = ['network_interface_associations', 'routes', 'route_table_associations', 'tags']
        ec2_resource_list = dir(self.ec2)
        camel_case_methods_list = [ method for method in ec2_resource_list if method[0].isupper() ]
        camel_case_method_dict = {}
        for camel_case_method in camel_case_methods_list:
            collection_method = self.build_collection_method_from_camel_method(camel_case_method=camel_case_method)
            if collection_method in ec2_resource_list:
                camel_case_method_dict[camel_case_method] =  collection_method
            elif collection_method in known_missiong_collection_methods_list:
                camel_case_method_dict[camel_case_method] =  None
            else:
                collection_method_not_found_message = 'WARNING: {} not found in ec2_resource_list for camel_case_method: {}'.format(collection_method, camel_case_method)
                print(collection_method_not_found_message)
        print(camel_case_method_dict)
        return camel_case_method_dict

    def get_state_method_for_resource(self, resource_type):
        print(resource_type)
        if resource_type == 'images':
            sample_resource_list = list(self.ec2.images.filter(Owners=['self']))
        else:
            sample_resource_list = list(getattr(self.ec2, resource_type).all())
        if sample_resource_list:
            sample_resource = sample_resource_list[0]
            print(dir(sample_resource))

    def repopulate_state_dict(self):
        camel_case_method_dict = self.build_resource_dict()
        for camel_case_method, collection_method in camel_case_method_dict.items():
            if collection_method:
                self.get_state_method_for_resource(resource_type=camel_case_method_dict[camel_case_method])

aws_object = Utility(aws_profile='dev', aws_region='us-east-1')
aws_object.repopulate_state_dict()

