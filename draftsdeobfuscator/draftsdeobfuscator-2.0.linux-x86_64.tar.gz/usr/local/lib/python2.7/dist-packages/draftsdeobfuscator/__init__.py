#! /usr/bin/env python

import boto3
import sys
from datetime import datetime 
from datetime import timedelta
import json
import argparse
import os
import math
import draftsutils

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--start_time', required=True, dest='start_time')
    parser.add_argument('--end_time', required=True, dest='end_time')
    parser.add_argument('--spot_instance_data', required=True, dest='spot_instance_data')

    args = parser.parse_args()

    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    month_ago_string = args.end_time
    month_ago_minus_hour_string = args.start_time

    user_spot_instance_data = json.loads(args.spot_instance_data)

    regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
    instance_types = ['m4.large']

    my_spot_instance_data = {}

    for region in regions:
        my_spot_instance_data[region] = {}
        for instance_type in instance_types:
            client = boto3.client('ec2', region_name=region,
                         aws_access_key_id = aws_access_key_id,
                         aws_secret_access_key = aws_secret_access_key)
            pag = client.get_paginator('describe_spot_price_history')
            params = {'EndTime': month_ago_string, 'StartTime': month_ago_minus_hour_string, 
                    'InstanceTypes': [instance_type], 'ProductDescriptions': ['Linux/UNIX']}
            iterator = pag.paginate(**params)
            result = draftsutils.get_by_az(draftsutils.get_by_instance_type(draftsutils.get_spot_prices(iterator))[instance_type])
            my_spot_instance_data[region][instance_type] = result

    
    for region in my_spot_instance_data.keys():
        for instance_type in my_spot_instance_data[region].keys():

            r = draftsutils.compare(my_spot_instance_data[region][instance_type], user_spot_instance_data[region][instance_type])

            for my_az in r.keys():
                user_azs = r[my_az]
                cur_score = float('-inf')
                cur_az = None
                for user_az in user_azs.keys():
                    score = user_azs[user_az]
                    if score > cur_score:
                        cur_score = score
                        cur_az = user_az
                print(my_az + " " +  cur_az)
    
