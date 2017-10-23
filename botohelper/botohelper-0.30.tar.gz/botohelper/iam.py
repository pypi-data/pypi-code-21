#!/usr/bin/env python
import sys
import os
import datetime
import boto3
import time
import vmtools

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Iam():
    """Class to manipulate aws iam resources

    public methods:

    instance variables:
    self.aws_profile
    self.aws_region
    self.session
    self.iam
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
        # aws iam object (mainly used for creating and modifying iam user, groups, etc)
        self.iam = self.session.resource('iam', region_name=self.aws_region)

    def does_group_exist(self, group_name):
        """Take group name if it exists return group object, if not return None
        keyword arguments:
        :type group_name: string
        :param group_name: the Name tag of the iam group
        """
        #doing the search with pure python is easier to follow instead of using boto3 filters
        list_of_groups = list(self.iam.groups.all())
        for group in list_of_groups:
            if group.name == group_name:
                return group
        return None
