#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime
from os.path import expanduser
import os.path
import sys

import click
import requests, json

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils


@click.command()
@click.option("--apikey", "-a", required=True, help="gocker user API key")
@click.option("--login", "-l", required=True, help="godocker login")
@click.option("--server", "-s", default="https://godocker.genouest.org", help="godocker server url")
@click.option("noCert", '--no-certificate', is_flag=True, help="no SSL verification")

def login(apikey, login, server, noCert):

    data=json.dumps({'user': login, 'apikey': apikey})

    auth = HttpUtils.http_post_request("/api/1.0/authenticate", data, server, {'Content-type': 'application/json', 'Accept': 'application/json'}, noCert)

    # if token is empty, quit program with warning message
    if not auth:
        print("wrong authentification, please check your informations")
        sys.exit(1)
    else:
        Auth.create_auth_file(apikey, login, server, noCert)

if __name__ == "__main__":
    login()
