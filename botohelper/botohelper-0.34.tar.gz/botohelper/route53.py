#!/usr/bin/env python
import sys
import os
import boto3
import time
import vmtools
import botohelper.botohelpermain

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Route53(botohelper.botohelpermain.Main):
    """Class to manipulate aws route53 resources

    public methods:
    get_route53_record
    get_hosted_zone_id
    modify_a_record

    instance variables:
    self.aws_profile
    self.aws_region
    self.session
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
        # route 53 aws client
        self.client_route53 = self.session.client('route53', region_name=self.aws_region)
        # create dict of avilable hosted zones
        self.hosted_zones_dict = {'private_zones': {}, 'public_zones': {} }
        for zone in self.client_route53.list_hosted_zones()['HostedZones']:
            if zone['Config']['PrivateZone']:
               self.hosted_zones_dict['private_zones'][zone['Name'].strip('.')] = zone['Id']
            else:
                self.hosted_zones_dict['public_zones'][zone['Name'].strip('.')] = zone['Id']

    def get_route53_record(self, fqdn, record_type='A', zone_group_type='public_zones'):
        """Take fqdn, record_type and zone_group_type return route53_record_dict if it exists, otherwise return None
        keyword arguments:
        :type fqdn: string
        :param fqdn: the new a record full qualified domain name
        :type record_type: string
        :param record_type: the type of DNS record
        :type zone_group_type: string
        :param zone_group_type: public_zones or private_zones
        """
        domain_name = self.get_domain_name_from_fqdn(fqdn)
        hosted_zone_id = self.get_hosted_zone_id(domain_name=domain_name, zone_group_type=zone_group_type)
        # if the domain isn't in route53 return None
        if not hosted_zone_id:
            return None
        fqdn_with_final_dot = fqdn+'.'
        # get records from host zone and make the first one be our record
        response = self.client_route53.list_resource_record_sets(HostedZoneId=hosted_zone_id, StartRecordName=fqdn_with_final_dot, StartRecordType=record_type)
        route53_record_dict = response['ResourceRecordSets'][0]
        # make sure the record found matches what we expect, if so return the dict, if not return None
        if route53_record_dict['Name'] == fqdn_with_final_dot:
            if route53_record_dict['Type'] == record_type:
                return route53_record_dict
            else:
                warning_message = "Warning: Found record for {} in zone: {}, but record type didn't match. Expecting: {}, Found: {}. Not deleting...".format(fqdn, zone_group_type, record_type, route53_record_dict['ResourceRecords']['Type'])
                print(warning_message)
                return None
        else:
            warning_message = "Warning: No record found for {} in zone: {}. Nothing to delete".format(fqdn, zone_group_type)
            print(warning_message)
            return None

    def get_hosted_zone_id(self, domain_name, zone_group_type='public_zones'):
        """Take domain_name and zone_group_type return route53 hosted_zone_id, if not found return None
        keyword arguments:
        :type domain_name: string
        :param domain_name: the domain name for the route53 hosted zone
        :type zone_group_type: string
        :param zone_group_type: public_zones or private_zones
        """
        if domain_name in self.hosted_zones_dict[zone_group_type]:
            hosted_zone_id = self.hosted_zones_dict[zone_group_type][domain_name]
            return hosted_zone_id
        else:
            domain_not_found_message = 'Warning: no hosted zone found for domain: {} in aws profile: {}'.format(domain_name, self.aws_profile)
            print(domain_not_found_message)
            return None

    def get_domain_name_from_fqdn(self, fqdn):
        """Take fqdn return domain_name (useful for determining the right hosted zone for route53)
        keyword arguments:
        :type fqdn: string
        :param fqdn: the new a record full qualified domain name
        """
        fqdn_list = fqdn.split('.')
        domain_name = '.'.join(fqdn_list[-2:])
        return domain_name

    def modify_a_record(self, fqdn, ip_address, action='create', ttl=300, zone_group_type='public_zones'):
        """Create an A record via route53
        keyword arguments:
        :type fqdn: string
        :param fqdn: the new a record full qualified domain name
        :type ip_address: string
        :param ip_address: the ip address for the new A record
        :type action: string
        :param action: create or delete the A record
        :type ttl: int
        :param ttl: the time to live in seconds
        :type zone_group_type: string
        :param zone_group_type: public_zones or private_zones
        """
        domain_name = self.get_domain_name_from_fqdn(fqdn)
        hosted_zone_id = self.get_hosted_zone_id(domain_name=domain_name, zone_group_type=zone_group_type)
        if not hosted_zone_id:
            no_record_to_modify_message = 'We have no dns record to modify, doing nothing'
            print(no_record_to_modify_message)
            return
        # set the correct a_record_action
        if action == 'create':
            a_record_action = 'UPSERT'
        elif action == 'delete':
            a_record_action = 'DELETE'
        else:
            exception_message = 'Fail: unrecognized value: {} for key word argument action. Accepted values are create or delete'.format(action)
            raise ValueError(exception_message)
        # uncomment for troubleshooting the record modification
        #print("""
        #self.client_route53.change_resource_record_sets(
        #    HostedZoneId={},
        #    ChangeBatch={{
        #    'Comment': 'Modification by script: pastor',
        #    'Changes': [
        #        {{
        #            'Action': {},
        #            'ResourceRecordSet': {{
        #                'TTL': {},
        #                'Name': {},
        #                'Type': 'A',
        #                'ResourceRecords': [
        #                    {{
        #                        'Value': {}
        #                        }},
        #                    ]
        #                }}
        #            }},
        #        ]
        #    }}
        #    )
        #    """.format(hosted_zone_id,a_record_action,ttl,fqdn,ip_address))

        # modify the record 
        self.client_route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
            'Comment': 'Modification by script: pastor',
            'Changes': [
                {
                    'Action': a_record_action,
                    'ResourceRecordSet': {
                        'TTL': ttl,
                        'Name': fqdn,
                        'Type': 'A',
                        'ResourceRecords': [
                            {
                                'Value': ip_address
                                },
                            ]
                        }
                    },
                ]
            }
            )
