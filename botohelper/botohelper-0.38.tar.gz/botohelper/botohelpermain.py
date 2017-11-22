#!/usr/bin/env python
import sys
import boto3
import vmtools

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Main():
    """Class to manipulate aws ec2 resources

    instance variables:
    self.aws_profile
    self.aws_region
    self.session
    self.client_ec2
    self.availability_zones_list
    """

    def __init__(self, aws_profile, aws_region):
        """set instance variables, set instance aws connections

        keyword arguments:
        :type aws_profile: string
        :param aws_profile: the profile to use from ~/.aws/credentials to connect to aws
        :type aws_region: string
        :param aws_region: the region to use for the aws connection object (all resources will be created in this region)
        """
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        # aws session
        self.session = boto3.Session(profile_name=self.aws_profile)
        # ec2 aws client
        self.client_ec2 = self.session.client('ec2', region_name=self.aws_region)
        # aws ec2 object (mainly used for creating and modifying resources)
        self.ec2 = self.session.resource('ec2', region_name=self.aws_region)
        # create a list of available availability zones
        availability_zones_state_dict = self.client_ec2.describe_availability_zones()
        self.availability_zones_list = []
        for availability_zone_dict in availability_zones_state_dict['AvailabilityZones']:
            if availability_zone_dict['State'] == 'available':
                self.availability_zones_list.append(availability_zone_dict['ZoneName'])
