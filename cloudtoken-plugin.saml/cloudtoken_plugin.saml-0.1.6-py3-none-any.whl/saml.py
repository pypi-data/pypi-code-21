# Plugin for cloudtoken.
# The plugin immediately prior should output a SAML assertion which this plugin will consume.
# It will then print out a list of Roles from which you can select. There are also filtering
# and refresh options available.
# Input: SAML Assertion
# Output: Credentials.

from __future__ import print_function
from datetime import datetime
from base64 import b64decode
from sys import version_info
import xml.etree.ElementTree as ET
import re
import logging
import boto3
import os
import json
import argparse

if str(version_info.major) == "2":
    input = raw_input  # noqa


class Plugin(object):
    def __init__(self, config):
        self._name = 'saml'
        self._description = 'Selection a Role from SAML.'
        self._cloudtoken_dir = "{0}/.config/cloudtoken".format(os.path.expanduser('~'))  # TODO: Pull from config.yaml
        self._cloudtoken_json_filename = "{0}/tokens.json".format(self._cloudtoken_dir)  # TODO: Pull from config.yaml
        self._config = config

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("-l",
                            "--list",
                            dest="list",
                            action="store_true",
                            help="List all roles available to the user then exit.")
        parser.add_argument("-f",
                            "--filter",
                            dest="filter",
                            default=defaults.get('filter', None),
                            help="Only show roles matching filter.")
        parser.add_argument("-n",
                            "--numbers-only",
                            dest="numbers_only",
                            action="store_true",
                            help="Only list role numbers. Useful for automation.")
        parser.add_argument("--refresh",
                            action="store_true",
                            help="Refresh tokens for last selected Role.")
        parser.add_argument("-r",
                            "--role-number",
                            default=defaults.get('role-number', None),
                            help="Specify a role without prompting you to select from the list.")
        return parser

    @staticmethod
    def filter_roles(pattern, roles):
        p = re.compile(r'{0}'.format(pattern), re.IGNORECASE)
        filtered_list = list()

        for b in range(1, len(roles) + 1):
            result = p.search(roles[b - 1][0])
            if result:
                filtered_list.append(roles[b - 1])

        return filtered_list

    def create_role_list(self, args, saml_response):
        saml_response = b64decode(saml_response)
        namespaces = {'ds': 'http://www.w3.org/2000/09/xmldsig#',
                      'html': 'http://www.w3.org/1999/xhtml',
                      'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                      'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                      'xs': 'http://www.w3.org/2001/XMLSchema',
                      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        saml = ET.fromstring(saml_response)
        a = saml.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute[@Name='https://aws.amazon.com/SAML/Attributes/Role']", namespaces=namespaces)  # noqa

        role_list = []
        for b in a.getchildren():
            arns = b.text.split(',')
            if ':saml-provider/' in arns[0]:
                role_list.append([arns[1], arns[0]])
            else:
                role_list.append([arns[0], arns[1]])

        if args.filter:
            role_list = self.filter_roles(args.filter, role_list)

        role_list.sort(key=lambda role: role[0])
        return role_list

    def list_roles(self, roles, numbers_only=False):
        for b in range(1, len(roles) + 1):
            if numbers_only:
                print("{0}".format(b))
            else:
                print("\t{0}. {1}".format(b, roles[b - 1][0]))

    def get_choice_from_roles(self, roles, args):
        choice = None
        if args.role_number and not args.list:
            if 1 <= int(args.role_number) <= len(roles):
                choice = int(args.role_number) - 1
            else:
                print("Invalid role number provided: {0}".format(args.role_number))

        while choice is None:
            print("Available roles to choose from:")
            self.list_roles(roles)
            print()
            if args.list:
                exit(0)

            selection = input("Enter number of role you want: ")

            try:
                if 1 <= int(selection) <= len(roles):
                    choice = int(selection) - 1
                    break
                else:
                    print("Select a valid option.")
            except ValueError:
                print("Select a valid option.")

        if not args.quiet:
            print("Using role {0}".format(roles[choice][0]))
        return choice

    @staticmethod
    def assume_role_with_saml(saml_response, role):
        client = boto3.client('sts')

        role_arn = role[0]
        principle_arn = role[1]

        temp_credentials = client.assume_role_with_saml(RoleArn=role_arn,
                                                        PrincipalArn=principle_arn,
                                                        SAMLAssertion=saml_response)

        logging.debug("AssumeRoleWithSaml Response: {0}".format(temp_credentials))

        credentials = {
            'AccessKeyId': temp_credentials['Credentials']['AccessKeyId'],
            'Expiration': temp_credentials['Credentials']['Expiration'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'LastRole': role_arn,
            'SAMLProvider': principle_arn,
            'SecretAccessKey': temp_credentials['Credentials']['SecretAccessKey'],
            'Token': temp_credentials['Credentials']['SessionToken'],
            'Type': 'AWS-HMAC',
            'Code': 'Success',
            'LastUpdated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'AccountId': role_arn.split(':')[4]
        }

        return credentials

    def execute(self, data, args, flags):
        if flags.get('daemon_mode', False):
            for d in data:
                if dict(d)['plugin'] == self._name:
                    last_role = dict(d)['data']['LastRole']
                    break
            args.filter = last_role

        # We expect the SAML response to be passed from the previously run plugin.
        try:
            saml_response = dict(data[-1])['data']
        except Exception:
            print("Unable to load SAML response from previous plugin. Exiting.")
            exit(1)
        logging.debug("SAMLResponse: {0}".format(b64decode(saml_response)))

        roles = self.create_role_list(args, saml_response)
        if not roles:
            print("No roles found in SAML Response.")
            exit(1)
        logging.debug("Roles: {0}".format(roles))

        if args.numbers_only:
            self.list_roles(roles, numbers_only=True)
            exit(0)

        if args.refresh:
            with open(self._cloudtoken_json_filename) as fh:
                token_json = json.loads(fh.read())
            selected_role = [token_json['LastRole'], token_json['SAMLProvider']]
        elif len(roles) == 1:
            # Don't want this to print every time in daemon mode.
            if flags.get('daemon_mode', False):
                if not args.quiet:
                    print("Using role {0}".format(last_role))
            else:
                if not args.quiet:
                    print("Auto selecting matching role: {0}".format(roles[0][0]))
            selected_role = roles[0]
        else:
            role_selection = self.get_choice_from_roles(roles, args)
            if len(roles) <= role_selection < 0:
                print("Invalid role number returned from get_choice_from_roles.")
                exit(1)

            selected_role = roles[role_selection]

        credentials = self.assume_role_with_saml(saml_response, selected_role)

        data.append({'plugin': self._name, 'data': credentials})
        return data
