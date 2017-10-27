# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import uuid
import re

from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qs

from tcell_agent.policies import TCellPolicy
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent

import logging

logger = logging.getLogger('tcell_agent').getChild(__name__)

import hmac
import hashlib
import sys


class HoneytokenPolicy(TCellPolicy):
    api_identifier = "exp-honeytokens"

    def __init__(self, policy_json=None):
        super(HoneytokenPolicy, self).__init__()
        self.cred_tokens = None
        self.token_salt = None
        if policy_json is not None:
            self.load_from_json(policy_json)

    def get_id_for_credential(self, username, password):
        if self.cred_tokens is None:
            return None
        token = self.create_credential_token(username, password)
        if token is not None:
            return self.cred_tokens.get(token)
        return None

    def create_credential_token(self, username, password, token_salt=None):
        if username is None or password is None:
            return None
        if token_salt is None:
            token_salt = self.token_salt
        if token_salt is None:  # still? well we can't hmac that
            return None
        try:
            username_enc = bytes(username, 'utf-8')
            token_salt_enc = bytes(token_salt, 'utf-8')
        except:
            username_enc = bytes(username)
            token_salt_enc = bytes(token_salt)
        passwordhmac = hmac.new(username_enc, str(password).encode('utf-8'), hashlib.sha512).hexdigest()
        combo = username + passwordhmac[:62]
        token = hmac.new(token_salt_enc, str(combo).encode('utf-8'), hashlib.sha256).hexdigest()
        return token

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        policy_data_json = policy_json.get("data")
        if policy_data_json:
            token_salt = policy_data_json.get("token_salt")
            if token_salt is not None:
                self.token_salt = token_salt
                credentials = policy_data_json.get("credentials")
                if credentials is not None:
                    self.cred_tokens = {}
                    for credential in credentials:
                        if credential.get("id") and credential.get("token"):
                            self.cred_tokens[credential.get("token")] = credential.get("id")
