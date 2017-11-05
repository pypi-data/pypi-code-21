#! /usr/bin/env python
import pdb

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
import json
from argparse import RawTextHelpFormatter

protocol = 'http://'
default_host = '169.231.235.152'
default_port = "80"

def get_drafts_credentials(sign_in):
    email = None
    password = None
    drafts_creds_path = os.path.join(expanduser("~"), '.drafts', 'credentials')
    if sign_in or not os.path.exists(drafts_creds_path):
        email = raw_input('Email:')
        password = getpass.getpass("Password for " + email + ":")
        if not os.path.exists(os.path.join(expanduser("~"), '.drafts')):
            os.mkdir(os.path.join(expanduser('~'), '.drafts'))
        with open(drafts_creds_path, 'wb') as f:
            f.write('email = ' + email + '\n')
            f.write('password = ' + password + '\n')
    else:
        email_reg = re.compile("email\s*=\s*(.+)")
        pass_reg = re.compile("password\s*=\s*(.+)")
        with open(drafts_creds_path, 'rb') as f:
            for line in f:
                email_res = email_reg.match(line)
                pass_res = pass_reg.match(line)
                if email_res != None:
                    email = email_res.groups()[0]
                if pass_res != None:
                    password = pass_res.groups()[0]
        if email == None or password == None:
            raise "email or password not present"
    return { 'email': email, 'password': password }

def build_url_base(host, port):
    use_extension = False
    if host == None:
        use_extension = True
    host = default_host if host == None else host
    port = default_port if port == None else port
    rv = protocol + host + ':' + port
    if use_extension == True:
        rv += "/auth_api"
    return rv

# assumes file exists
def data_from_file(file):
    data = None
    with open(file) as f:
        data = json.load(f)
    rv = []
    for region in data:
        for az in data[region]:
            for instance_type in data[region][az]["instance_types"]:
                rv.append({
                    "region": region,
                    "az": az,
                    "instance_type": instance_type
                })
    return rv

def sign_in(email, password, url_base):
    try:
        jwt_response = requests.post(url_base + '/auth', json = { 'username': email, 'password': password }  )
        return jwt_response.json()['access_token']
    except KeyError:
        print("\nIncorrect DrAFTS credentials. Run again with --sign_in")
        sys.exit(1)
    except ValueError:
        print("\nServer Error")
        sys.exit(1)

def get_data():
    return '/data'

def query_server(url_base, url_extension, jwt):
    response = None
    if jwt != None:
        headers = {'Authorization' : 'JWT ' + jwt}
        response = requests.get(url_base + url_extension, headers = headers)
    else:
        response = requests.get(url_base + url_extension)

    return response.json()

def post_server(url_base, url_extension, json={}, jwt=None):
    if jwt != None:
        headers = {'Authorization' : 'JWT ' + jwt}
        response = requests.post(url_base + url_extension, headers = headers, json = json)
    else:
        response = requests.post(url_base + url_extension, json = json)
    return response.json()

# assumes valid file
def process_aws_creds_file(creds_path, user):
    content = None
    with open(creds_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    users = {}
    user_is = []
    for line_i, val in enumerate(content):
        if not len(val.strip()) == 0:
            if val[0] == '[' and val[-1] == ']':
                users[val[1:-1]] = line_i
                user_is.append(line_i)
    user_is.sort()
    line_n = users[user]
    end_index = len(user_is) - 1
    end = end_index
    if user_is.index(line_n) + 1 < end_index:
        end = user_is[user_is.index(line_n) + 1]
    else:
        end = len(content)
    access_key_re = re.compile("aws_access_key_id\s*=\s*(.+)")
    secret_re = re.compile("aws_secret_access_key\s*=\s*(.+)")
    acces_key = None
    secret = None
    for line_i in xrange(line_n, end):
        ak_res = access_key_re.match(content[line_i])
        s_res = secret_re.match(content[line_i])
        if ak_res != None:
            access_key = ak_res.groups()[0]
        if s_res != None:
            secret = s_res.groups()[0]
    rv = {}
    rv[user] = {}
    rv[user]['access_key'] = access_key
    rv[user]['secret'] = secret
    return rv

def get_spot_prices(iterator):
    spot_prices = []
    for page in iterator:
        for spotdata in page['SpotPriceHistory']:
            spot_prices.append(spotdata)
    return spot_prices

def get_by_instance_type(spot_prices):
    by_instance_types = {}
    for sp in spot_prices:
        instance_type_data = by_instance_types.get(sp['InstanceType'], [])
        instance_type_data.append(sp)
        by_instance_types[sp['InstanceType']] = instance_type_data
    return by_instance_types

def get_by_az(instance_type_data):
    by_az = {}
    for data_point in instance_type_data:
        data_point['Timestamp'] = data_point['Timestamp'].strftime("%Y-%m-%dT%H:%M:%S")
        az_point = by_az.get(data_point['AvailabilityZone'], [])
        az_point.append(data_point)
        by_az[data_point['AvailabilityZone']] = az_point
    return by_az

def get_parser(sign_in = True, all = True, host = True, port = True, no_sign_in = True, file = True):
    json_doc = '''
    {
      region_name: {
        az_name:{
          instance_types:[...]
        },
        ...
      },
    ...
    }
    '''

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    if sign_in != False:
        parser.add_argument('-s', '--sign_in', action='store_true', default=False, help='sign in and overwrite current credentials at ~/.drafts/credentials')
    if all != False:
        parser.add_argument('-a', '--all', action='store_true', default=False, help='download all data on the server')
    if host != False:
        parser.add_argument('--host', required=False, dest='host', help='host to query drafts server')
    if port != False:
        parser.add_argument('-p', '--port', required=False, dest='port', help='port the server listens on')
    if no_sign_in != False:
        parser.add_argument('-n', '--no_sign_in', action='store_true', default=False, help="don't use the provided user credentials, the results won't be specific to your az mapping")
    if file != False:
        parser.add_argument('-f', '--file', required=False, dest='file', help='json document used to specify data to pull from server of form \n' + json_doc)
    return parser

def compare(res1, res2):
    results = {}
    for az1 in res1.keys():
        data_points1 = res1[az1]
        result = {}
        for az2 in res2.keys():
            data_points2 = res2[az2]
            matches = 0
            for dp1 in data_points1: 
                for dp2 in data_points2:
                    if (dp1['SpotPrice'] == dp2['SpotPrice'] and
                        dp1['Timestamp'] == dp2['Timestamp']):
                        matches += 1
            result[az2] = matches / float(len(data_points1))
        results[az1] = result
    return results
