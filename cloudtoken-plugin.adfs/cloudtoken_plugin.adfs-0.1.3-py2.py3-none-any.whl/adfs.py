# Microsoft ADFS plugin for cloudtoken.
#
# You will need to add the key 'adfs_url' with the value being the URL for your ADFS IdP, for example:
#
# adfs_url: !!str 'https://myserver.mydomain.com/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'
#
# Author: Shane Anderson (sanderson@atlassian.com)

import xml.etree.ElementTree as Et
import re
import requests
import argparse


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = 'adfs'
        self._description = 'Authenticate against Microsoft ADFS.'

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        return parser

    def execute(self, data, args, flags):
        url, host = (None, None)

        try:
            url = self._config['adfs_url']
        except KeyError:
            print("Configuration key 'adfs_url' not found. Exiting.")
            exit(1)

        try:
            host = re.search(r'(https?://[\w\-.]+)/', url).group(1)
        except AttributeError:
            print("Configuration key 'adfs_url' value does not seem to be a http(s) URL. Exiting.")
            exit(1)

        requests.packages.urllib3.disable_warnings()  # Disable warning for self signed certs.
        session = requests.session()

        username = args.username
        password = args.password

        # We check for an error status here, but ADFS 2.0 seems to give back 200's even if you are unauthorised...
        r = session.get(url, verify=False, auth=(username, password), allow_redirects=False)
        r.raise_for_status()
        r = session.get(r.headers['location'], auth=(username, password), verify=False, allow_redirects=False)
        r.raise_for_status()
        r = session.get(host + r.headers['location'], verify=False, auth=(username, password), allow_redirects=False)
        r.raise_for_status()

        namespaces = {'ds': 'http://www.w3.org/2000/09/xmldsig#',
                      'html': 'http://www.w3.org/1999/xhtml',
                      'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                      'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                      'xs': 'http://www.w3.org/2001/XMLSchema',
                      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

        try:
            saml_response = Et.fromstring(r.text).find(".//input[@name='SAMLResponse']",
                                                       namespaces=namespaces).attrib["value"]
        except AttributeError:
            print("Unable to login to ADFS IdP. Exiting.")
            exit(1)
        else:
            data.append({'plugin': self._name, 'data': saml_response})
            return data
