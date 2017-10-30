from future.builtins.misc import input
from oauth2client import client

import json
import webbrowser
import argparse
import os
import math
import datetime

from datetime import timedelta



def format_as_credentials(input_secrets, credentials):
  expiry_date = datetime.datetime.now()+timedelta(hours=1)
  expiry_date_formatted = expiry_date.strftime('%Y-%m-%d')+'T'+ expiry_date.strftime('%H:%M:%S') + 'Z'
  secrets = {
    '_module': 'oauth2client.client',
    'token_expiry': expiry_date_formatted,
    'token_uri': 'https://accounts.google.com/o/oauth2/token',
    'invalid': False,
    'token_response':{
      'access_token': credentials.access_token,
      'token_type': 'Bearer',
      'expires_in': 3600,
    },
    'user_agent': None,
    'id_token': None,
    'revoke_uri': "https://accounts.google.com/o/oauth2/revoke",
    '_class': 'OAuth2Credentials',
    'access_token': credentials.access_token,
    'refresh_token': credentials.refresh_token,
    'client_id': input_secrets['installed']['client_id'],
    'client_secret': input_secrets['installed']['client_secret'],
  }
  return secrets

def format_as_client_secret(input_secrets, credentials):
  created_time = int(math.floor((datetime.datetime.now()-datetime.datetime.utcfromtimestamp(0)).total_seconds()))
  secrets = {
    'installed': {
        "client_id": input_secrets['installed']['client_id'],
        "project_id": input_secrets['installed']['project_id'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": input_secrets['installed']['client_secret'],
        "redirect_uris": [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost"
        ]
    },
    'access_token': credentials.access_token,
    'refresh_token': credentials.refresh_token,   
    'expires_in': 3600,
    'created': created_time
  }
  # @change: also add 'created' attribute
  return secrets


class Credulous:
  """
    Class created to complete the oauth2 flow with a standard brainlabs
    client secret and scopes file
  """

  JSON = 'json'
  BROWSER = 'browser'
  LINK = 'link'
  DEFAULT_FILE_FORMAT = JSON
  DEFAULT_INTERACTION = LINK

  def __init__(self, client_secret_path, scopes_path, 
    file_format=None, format_secrets=format_as_client_secret, output_file=None):
    self.client_secret_path = client_secret_path
    self.scopes_path = scopes_path
    self.file_format = file_format or self.DEFAULT_FILE_FORMAT
    self.output_file = output_file or client_secret_path
    self.format_secrets = format_secrets

  def authenticate(self):
    input_secrets = self._load(self.client_secret_path)
    scopes = self._load(self.scopes_path)
    credentials = self._create_credentials(input_secrets, scopes)
    secrets = self.format_secrets(input_secrets, credentials)
    if 'developer_token' in input_secrets:
      secrets['developer_token'] = input_secrets['developer_token']
    if 'user_agent' in input_secrets:
      secrets['user_agent'] = input_secrets['user_agent']
    if 'customer_id' in input_secrets:
      secrets['customer_id'] = input_secrets['customer_id']
    if 'account_id' in input_secrets:
      secrets['account_id'] = input_secrets['account_id']
    self._store_secrets(secrets)
    print("Credentials saved in " + self.output_file)

  def _load(self, file_path):
    if self.file_format == self.JSON:
      with open(file_path) as fh:
        try:
          return json.loads(fh.read())
        except ValueError:
          print("{} contains invalid JSON".format(file_path))
          raise

  def _create_credentials(self, secrets, scopes):
    flow = self._make_flow(secrets, scopes)
    auth_uri = flow.step1_get_authorize_url()
    auth_code = self._interact(auth_uri)
    credentials = flow.step2_exchange(auth_code)
    return credentials

  def _make_flow(self, secrets, scopes):
    flow = client.OAuth2WebServerFlow(
      client_id=secrets['installed']['client_id'],
      client_secret=secrets['installed']['client_secret'],
      scope=scopes['scopes']['google'],
      user_agent='Brainlabs',
      redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    return flow

  def _interact(self, uri):
    if self.DEFAULT_INTERACTION == self.LINK:
      print("Click here: ")
      print(uri)
    else:
      webbrowser.open(uri)
    auth_code = input('Enter the auth code: ')
    return auth_code

  def _store_secrets(self, secrets):
    with open(self.output_file, 'w') as fh:
      json.dump(secrets, fh)
