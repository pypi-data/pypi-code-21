from __future__ import absolute_import, division, print_function, unicode_literals

import boto3
import json
import os
import sys

TIROS_VERSION = '1.0'

CONTENT_TYPE = 'application/json'
METHOD = 'POST'

VERBOSE = False

try:
    import botocore_amazon.monkeypatch
except ImportError:
    pass


def vprint(x):
    if VERBOSE:
        print(str(x))


def eprint(s):
    print(s)
    sys.exit(1)


def new_session(profile_name=None, region_name=None):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    if not session.get_credentials():
        print("Can't find AWS credentials.  Please set up your credentials as described here:")
        eprint("    http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html")
    if not session.region_name:
        print("Can't find a region for profile: " + session.profile_name)
        print("Is there a default set in ~/.aws/config?")
        print("Please set up your credentials as described here:")
        eprint("  http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html")
    return session


def file_contents(path):
    if os.path.exists(path):
        with open(path) as fd:
            return fd.read()
    else:
        # Don't use FileNotFoundError, which doesn't exist in Python2
        raise IOError('File not found: ' + path)


def quote(s):
    return '"' + s + '"'


def json_encoder(obj):
    """JSON serializer for objects not serializable by default json code"""
    if type(obj) == bytes:
        return obj.decode('utf-8')
    raise TypeError("Type not serializable")


def pretty(x):
    return json.dumps(x, indent=2, sort_keys=True, default=json_encoder)


def canonical(x):
    return json.dumps(x, sort_keys=True, default=json_encoder)


def assume_role_session(session, role_arn, region=None):
    """
    :param session: An existing boto Session
    :param role_arn: An IAM role to assume
    :param region: The region for the new Session, defaults to region of
    existing session.
    :return: A Session with the assumed role.
    """
    sts = session.client('sts')
    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='tiros',  # arbitrary
    )
    if 'Credentials' not in creds:
        eprint("Couldn't assume role: " + role_arn)
    cs = creds['Credentials']
    token = cs['SessionToken'] if 'SessionToken' in cs else None
    if not region:
        region = session.region_name
    return boto3.Session(
        aws_access_key_id=cs['AccessKeyId'],
        aws_secret_access_key=cs['SecretAccessKey'],
        aws_session_token=token,
        region_name=region)


def change_session_region(session, region):
    if region == session.region_name:
        return session
    creds = session.get_credentials()
    return boto3.Session(aws_access_key_id=creds.access_key,
                         aws_secret_access_key=creds.secret_key,
                         aws_session_token=creds.token,
                         region_name=region)


def account(session):
    return session.client('sts').get_caller_identity().get('Account')
