#! /usr/bin/env python

# coding: utf-8

# In[1]:

import boto3
import sys
from datetime import datetime 
from datetime import timedelta
import requests
import json
import urllib2
import argparse
import getpass
from botocore.exceptions import ClientError
import os.path
from os.path import expanduser
import re
import draftsutils

def main():
    
    #parser.add_argument('--sign_in', action='store_true', default=False)
    #
    #
    #aws_args = parser.parse_args()

    parser = draftsutils.get_parser(file = False, all = False, no_sign_in = False)
    parser.add_argument('--user', required=False, dest='user')
    parser.add_argument('--aws_access_key_id', required=False, dest='aws_access_key_id')
    parser.add_argument('--aws_secret_access_key', required=False, dest='aws_secret_access_key') 
    parser.add_argument("--do_you_see_me", required=False)

    aws_args = parser.parse_args()

    user = aws_args.user
    if aws_args.user == None:
        print "no user provided, using default user"
        user = 'default'
    aws_access_key_id = None
    aws_secret_access_key = None
    aws_creds_path = os.path.join(expanduser("~"), '.aws', 'credentials')
    if not os.path.exists(aws_creds_path):
        if aws_args.aws_access_key_id != None and aws_args.aws_access_key_id != None:
            aws_access_key_id = aws_args.aws_access_key_id
            aws_secret_access_key = aws_args.secret_access_key
        else:
            print "no credential file present, and no commandline arguments provided"
            return
    else:
        try:
            aws_creds_dict = draftsutils.process_aws_creds_file(aws_creds_path, user)
            aws_access_key_id = aws_creds_dict[user]['access_key']
            aws_secret_access_key = aws_creds_dict[user]['secret']
        except:
            print "either there is an error with your ~/.aws/credentials file or the specified user doesn't have aws_access_key_id and aws_secret_access_key specified"
            return

    sign_in_result = None
    try:
        sign_in_result = draftsutils.get_drafts_credentials(aws_args.sign_in)
    except:
        print("Error with ~/.drafts/credentials please run draftsupdate with --sign_in")
        return

    email = sign_in_result['email']
    password = sign_in_result['password']

    month_ago = datetime.now() - timedelta(days = 30)
    month_ago_2 = month_ago - timedelta(days = 30)
    month_minus_hour = month_ago - timedelta(hours = 1)

    month_ago_string = month_ago.strftime("%Y-%m-%dT%H:%M:%S")
    month_ago_2_string = month_ago_2.strftime("%Y-%m-%dT%H:%M:%S")
    month_minus_hour_string = month_minus_hour.strftime("%Y-%m-%dT%H:%M:%S")


    regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
    instance_types = ['m4.large']

    metadata = {'end-time': month_ago_string, 'start-time': month_minus_hour_string}
    results = {'metadata': metadata}
    spot_instance_data = {}

    try:
        for region in regions:
            spot_instance_data[region] = {}
            for instance_type in instance_types:
                client = boto3.client('ec2', region_name=region,
                             aws_access_key_id = aws_access_key_id,
                             aws_secret_access_key = aws_secret_access_key)
                pag = client.get_paginator('describe_spot_price_history')
                params = {'EndTime': month_ago_string, 'StartTime': month_minus_hour_string, 
                        'InstanceTypes': [instance_type], 'ProductDescriptions': ['Linux/UNIX']}
                iterator = pag.paginate(**params)
                result = draftsutils.get_by_az(draftsutils.get_by_instance_type(draftsutils.get_spot_prices(iterator))[instance_type])
                spot_instance_data[region][instance_type] = result
                sys.stdout.flush()
                sys.stdout.write("\r" + region + ": " + instance_type)

    except (ClientError):
        print("Invalid AWS credentials")

    results['spot-instance-data'] = spot_instance_data

    url_base = draftsutils.build_url_base(aws_args.host, aws_args.port)

    jwt = None
    try:
        jwt = draftsutils.sign_in(email, password, url_base)
    except ValueError:
        print("\nIncorrect DrAFTS credentials. Run again with --sign_in")
        return


    try:
        success = draftsutils.post_server(url_base, '/users/update_az_map', results, jwt)

        if success:
            print("\nSuccessfully updated!")
        else:
            print("\nSomething went wrong. This feature is experimental. Please email wlbberman@gmail.com to notify us")

    except ValueError:
        print("\nIncorrect DrAFTS credentials")


if __name__ == "__main__":
    main()
