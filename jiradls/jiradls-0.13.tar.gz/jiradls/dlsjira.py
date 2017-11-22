from __future__ import absolute_import, division, print_function

import json
import os
import sys

_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.jira')
if not os.path.exists(_CONFIG_DIR):
  os.makedirs(_CONFIG_DIR, 0o700)
_CONFIG_PATH = os.path.join(_CONFIG_DIR, 'config.json')
_DLSCONFIG_PATH = os.getenv('JIRA_DLSCONFIG', 'dls-configuration.json')
try:
  with open(_CONFIG_PATH, 'r') as fh:
    _configuration = json.load(fh)
except IOError:
  _configuration = {}
with open(_DLSCONFIG_PATH, 'r') as fh:
  _dlsconfig = json.load(fh)

def _oauth_authenticate():
  import requests
  from six.moves.urllib.parse import parse_qsl
  from oauthlib.oauth1 import SIGNATURE_RSA
  from requests_oauthlib import OAuth1
  import time
  import webbrowser

  verify = _dlsconfig['server'].startswith('https')

  print("Connecting to JIRA...")

  # step 1: get request tokens
  oauth = OAuth1(_dlsconfig['consumer-key'], signature_method=SIGNATURE_RSA, rsa_key=_dlsconfig['application-key'])
  r = requests.post(_dlsconfig['server'] + '/plugins/servlet/oauth/request-token', verify=verify, auth=oauth)
  request = dict(parse_qsl(r.text))
  request_token = request['oauth_token']
  request_token_secret = request['oauth_token_secret']

  # step 2: prompt user to validate
  auth_url = '{}/plugins/servlet/oauth/authorize?oauth_token={}'.format(
      _dlsconfig['server'], request_token)
  savout = os.dup(1)
  os.close(1)
  os.open(os.devnull, os.O_RDWR)
  saverr = os.dup(2)
  os.close(2)
  os.open(os.devnull, os.O_RDWR)
  try:
    webbrowser.open_new(auth_url)
  finally:
    os.dup2(savout, 1)
    os.dup2(saverr, 2)
  print("A browser window should open to authorize the OAuth request.\nAlternatively please go to this URL:\n\t{}".format(auth_url))

  # step 3: wait for access tokens for validated user
  oauth = OAuth1(_dlsconfig['consumer-key'],
                 signature_method=SIGNATURE_RSA,
                 rsa_key=_dlsconfig['application-key'],
                 resource_owner_key=request_token,
                 resource_owner_secret=request_token_secret
                 )

  timeout = time.time() + 300 # do not wait longer than 5 minutes
  in_limbo = lambda x: x.get('oauth_problem') == 'permission_unknown'
  access = { 'oauth_problem': 'permission_unknown' }
  while in_limbo(access):
    r = requests.post(_dlsconfig['server'] + '/plugins/servlet/oauth/access-token', verify=verify, auth=oauth)
    access = dict(parse_qsl(r.text))
    if in_limbo(access):
      time.sleep(1)

  if access.get('oauth_problem'):
    print("\nJIRA access not granted")
    sys.exit(1)

  # step 4: all done.
  print("Access tokens received.\n")
  return {
    'access_token': access['oauth_token'],
    'access_token_secret': access['oauth_token_secret'],
  }

def _save_configuration():
  with open(_CONFIG_PATH, 'w') as fh:
    os.chmod(_CONFIG_PATH, 0o600)
    json.dump(_configuration, fh)

def DLSJIRA():
  '''Returns a JIRA object that is authenticated against the Diamond JIRA instance.'''
  options = { 'server': _dlsconfig['server'] }

  oauth = {
    'consumer_key': _dlsconfig['consumer-key'],
    'key_cert': _dlsconfig['application-key'],
  }
  try:
    oauth.update({ k: _configuration[k] for k in ('access_token', 'access_token_secret') })
  except KeyError:
    # not yet authenticated with JIRA
    _configuration.update(_oauth_authenticate())
    _save_configuration()
    oauth.update({ k: _configuration[k] for k in ('access_token', 'access_token_secret') })

  import jira
  try:
    return jira.JIRA(options=options, oauth=oauth)
  except jira.exceptions.JIRAError as e:
    if e.status_code == 401 and 'token_rejected' in e.text:
      # authentication token probably revoked. Renew and try once more.
      _configuration.update(_oauth_authenticate())
      _save_configuration()
      oauth.update({ k: _configuration[k] for k in ('access_token', 'access_token_secret') })
      return jira.JIRA(options=options, oauth=oauth)
