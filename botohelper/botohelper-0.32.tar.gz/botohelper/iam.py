#!/usr/bin/env python
import sys
import os
import datetime
import boto3
import time
import vmtools
import botohelpermain

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Iam(botohelpermain.Main):
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
        super().__init__(aws_profile=aws_profile, aws_region=aws_region)
        # aws iam object (mainly used for creating and modifying iam user, groups, etc)
        self.iam = self.session.resource('iam', region_name=self.aws_region)

    def get_iam_object_from_name(self, tag_name, object_type, fail_condition=None):
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
        filters = [{'Name':'tag:Name', 'Values':[tag_name]}]
        # filter all object of that type by our tag name and other stuff
        result = list(getattr(self.iam, object_type_plural).filter(Filters=filters))
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
                print(fail_on_exists_message)
                sys.exit(1)
            aws_object = None
        return aws_object

    def get_group_from_name(self, group_name):
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
