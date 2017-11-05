#! /usr/bin/env python

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
import draftsutils

import pdb

def main():

    aws_args = draftsutils.get_parser().parse_args()

    try:
        sign_in_result = draftsutils.get_drafts_credentials(aws_args.sign_in)
    except:
        print("Error with ~/.drafts/credentials please run draftsdownload with --sign_in")
        return

    email = sign_in_result['email']
    password = sign_in_result['password']

    if aws_args.file == None and aws_args.all == False:
        print('Please specify either --file or --all')
        return

    url_base = draftsutils.build_url_base(aws_args.host, aws_args.port)

    url_extension = draftsutils.get_data()
    data = None
    if aws_args.all == False:
        try:
            data = draftsutils.data_from_file(aws_args.file)
        except:
            print("problem with file: " + aws_args.file)
            return

    jwt = None
    if aws_args.no_sign_in == False:
        try:
            jwt = draftsutils.sign_in(email, password, url_base)
        except KeyError:
            print("\nIncorrect DrAFTS credentials. Run again with --sign_in")
            return
        except ValueError:
            print("\nServer Error")
            return

    try:
        json = draftsutils.post_server(url_base, url_extension, data, jwt)
        print json
    except:
        print "Server error"


if __name__ == "__main__":
    main()
