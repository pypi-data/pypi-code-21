#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
from builtins import *
import sys
import boto3
import logging
import botocore
import os
import yaml
import re
import pipes
import argparse
from datetime import datetime

AWSAUTH_DIR = os.environ['HOME'] + "/.awsauth"
CONFIG_FILE = AWSAUTH_DIR + "/config.yml"
CREDENTIALS_FILE = AWSAUTH_DIR + "/credentials.yml"

# logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.propagate = False
logger.addHandler(ch)

def read_or_init_config(file, profile):
    data = {}
    if not os.path.isdir(AWSAUTH_DIR):
        os.mkdir(AWSAUTH_DIR)

    try:
        with open(file, 'r') as config_file:
            data = yaml.load(config_file)

    except IOError:
        with open(file, 'w') as config_file:
            mfa_name = input("[{0}] Please enter MFA device name: ".format(profile))
            data[profile] =  {
                "mfa_name": mfa_name
            }
            yaml.dump(data, config_file, default_flow_style=False)
        os.chmod(file, 0o600)

    return data

def write_yaml_file(file, data):
    with open(file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    os.chmod(file, 0o600)


def read_yaml_file(file):
    try:
        with open(file, 'r') as f:
            return yaml.load(f)
    except:
        return {}

def validate_mfa_name(name):
    return re.match(r'^arn:aws:iam::[0-9]+:mfa/[a-zA-Z-\.,@]+$', name)

def session_expired(d1, d2):
    if d1 is not None:
        return int((d1 - d2).total_seconds())
    return -1

def rotate_access_key(client, access_key):
    credentials = {}
    for keys in client.list_access_keys()['AccessKeyMetadata']:
        if keys['AccessKeyId'] != access_key:
            client.delete_access_key(AccessKeyId=keys['AccessKeyId'])
    credentials = client.create_access_key()
    client.delete_access_key(AccessKeyId=access_key)
    return credentials

def print_environment(aws_access_key, aws_secret_access_key, aws_session_token):
        print("export AWSAUTH=1")
        print("export AWS_ACCESS_KEY_ID={0}".format(pipes.quote(str(aws_access_key))))
        print("export AWS_SECRET_ACCESS_KEY={0}".format(pipes.quote(str(aws_secret_access_key))))
        print("export AWS_SESSION_TOKEN={0}".format(pipes.quote(str(aws_session_token))))
        print("export AWS_SECURITY_TOKEN={0}".format(pipes.quote(str(aws_session_token))))

def print_environment_disabled(aws_access_key_id, aws_secret_access_key):
        print("unset AWSAUTH")
        print("unset AWS_SESSION_TOKEN")
        print("unset AWS_SECURITY_TOKEN")
        print("unset AWS_SESSION_EXPIRATION")
        if aws_access_key_id and aws_secret_access_key:
            print("export AWS_ACCESS_KEY_ID={0}".format(pipes.quote(str(aws_access_key_id))))
            print("export AWS_SECRET_ACCESS_KEY={0}".format(pipes.quote(str(aws_secret_access_key))))
        else:
            print("unset AWS_ACCESS_KEY_ID")
            print("unset AWS_SECRET_ACCESS_KEY")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', help='AWS profile', default='default')
    parser.add_argument('--duration', help='Number of seconds for the credentials to be active')
    parser.add_argument('--show-expiration', help='Shows STS key pair expiration time in seconds', action='store_true')
    parser.add_argument('--refresh', help='Refresh AWS credentials', action='store_true')
    parser.add_argument('--token', help='Specify MFA token', default='')
    parser.add_argument('--disable', help='Disable awsauth and restore AWS key pair', action='store_true')
    parser.add_argument('--rotate', help='Rotate AWS key pair', action='store_true')

    args = parser.parse_args()

    if args.duration == None:
        args.duration = 9 * 3600

    # load credentials file
    credentials = read_yaml_file(CREDENTIALS_FILE)
    if credentials.get(args.profile) == None:
        credentials[args.profile] = {}

    if args.disable:
        if args.profile in credentials:
            print_environment_disabled(credentials[args.profile].get('aws_access_key_id'), credentials[args.profile].get('aws_secret_access_key'))
            sys.exit(0)
        else:
            logger.error("Profile does not exist in: {0}".format(CREDENTIALS_FILE))
            sys.exit(1)

    data = read_or_init_config(CONFIG_FILE, args.profile)
    if data is None:
        logger.error("Incorrect/empty config file {0}".format(CONFIG_FILE))
        sys.exit(1)

    if args.profile not in data:
            mfa_name = input("[{0}] Please enter MFA device name: ".format(args.profile))
            data[args.profile] =  {
                "mfa_name": mfa_name
            }
            write_yaml_file(CONFIG_FILE, data)

    if validate_mfa_name(data[args.profile]['mfa_name']) is None:
        logger.error("MFA name validation error {0}".format(CONFIG_FILE))
        sys.exit(1)

    aws_access_key_id = None
    aws_secret_access_key = None


    if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
        if not os.environ.get('AWSAUTH'):
            aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    if os.environ.get('AWS_ACCESS_KEY_ID'):
        del os.environ['AWS_ACCESS_KEY_ID']

    if os.environ.get('AWS_SECRET_ACCESS_KEY'):
        del os.environ['AWS_SECRET_ACCESS_KEY']

    if os.environ.get('AWS_PROFILE'):
        del os.environ['AWS_PROFILE']

    if os.environ.get('AWS_SESSION_TOKEN'):
        del os.environ['AWS_SESSION_TOKEN']

    if os.environ.get('AWS_SECURITY_TOKEN'):
        del os.environ['AWS_SECURITY_TOKEN']

    os.environ['AWS_PROFILE'] = args.profile
    awsauth_enabled = os.environ.get('AWSAUTH')


    if aws_access_key_id and aws_secret_access_key and awsauth_enabled != 1:
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
        credentials[args.profile].update({
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key
        })

    if args.profile in credentials and args.show_expiration:
        s = session_expired(credentials[args.profile].get('sts_aws_session_expiration'), datetime.utcnow())
        if s < 0:
            logger.info("Session token has expired")
        else:
            logger.info("Session token is expiring in {0} seconds".format(s))
        sys.exit(1)

    if  credentials.get(args.profile) is None or \
        credentials[args.profile].get('sts_aws_session_expiration') is None or \
        session_expired(credentials[args.profile].get('sts_aws_session_expiration'), datetime.utcnow()) < 10 or \
        args.refresh:
        # session token has expired, get a new one
        try:
            if credentials.get(args.profile) and \
                credentials[args.profile].get('aws_access_key_id') and \
                credentials[args.profile].get('aws_secret_access_key'):
                os.environ['AWS_ACCESS_KEY_ID'] = credentials[args.profile]['aws_access_key_id']
                os.environ['AWS_SECRET_ACCESS_KEY'] = credentials[args.profile]['aws_secret_access_key']

            session = boto3.session.Session()
            client = session.client('sts')
            if args.token:
                my_token = args.token
            else:
                my_token = input("[{0}] Please type in your MFA token: ".format(args.profile))
            response = client.get_session_token(
                DurationSeconds = int(args.duration),
                SerialNumber = data[args.profile]['mfa_name'],
                TokenCode=str(my_token)
            )

            aws_access_key_id = response['Credentials']['AccessKeyId']
            aws_secret_access_key = response['Credentials']['SecretAccessKey']
            aws_session_token = response['Credentials']['SessionToken']
            aws_session_expiration = response['Credentials']['Expiration']

            credentials[args.profile].update({
                'sts_aws_access_key_id': aws_access_key_id,
                'sts_aws_secret_access_key': aws_secret_access_key,
                'sts_aws_session_token': aws_session_token,
                'sts_aws_session_expiration': aws_session_expiration
            })

            if args.rotate:
                session_credentials = session.get_credentials()
                session_credentials = rotate_access_key(session.client('iam'), session_credentials.access_key)
                credentials[args.profile]['aws_access_key_id'] = session_credentials['AccessKey']['AccessKeyId']
                credentials[args.profile]['aws_secret_access_key'] = session_credentials['AccessKey']['SecretAccessKey']

            write_yaml_file(CREDENTIALS_FILE, credentials)
            print_environment(aws_access_key_id, aws_secret_access_key, aws_session_token)

        except botocore.exceptions.ClientError as e:
            logger.error("Error calling an API:\n{0}".format(e))
            sys.exit(1)
        except botocore.exceptions.NoCredentialsError as e:
            logger.error("Error with credentials:\n{0}".format(e))
            sys.exit(1)
    else:
        aws_access_key_id = credentials[args.profile]['sts_aws_access_key_id']
        aws_secret_access_key = credentials[args.profile]['sts_aws_secret_access_key']
        aws_session_token = credentials[args.profile]['sts_aws_session_token']
        print_environment(aws_access_key_id, aws_secret_access_key, aws_session_token)

if __name__ == '__main__':
    sys.exit(main())
