import os, base64, sys

class BasicAuth:
 def __init__(self, failfile=None):
  self.login=None
  self.password=None
  self.realm='Authentication'
  self.fetched=False
  self.failed=False
  self.failfile=failfile

 def set_default_login(self, login):
  if not self.fetched:
   self.login=login
 def set_default_password(self, password):
  if not self.fetched:
   self.password=password
 def set_realm(self, realm):
  self.realm = realm

 def get_login(self):
  if self.failed:
   return None
  self.fetch()
  return self.login
 def get_password(self):
  if self.failed:
   return None
  self.fetch()
  return self.password

 def fetch(self):
  if self.fetched:
   return
  print('WWW-Authenticate: Basic realm="%s"' % (self.realm))
  if not 'HTTP_AUTHORIZATION' in os.environ:
   self.set_failed()
   return
  http_auth = os.environ['HTTP_AUTHORIZATION']
  if http_auth == '':
   self.set_failed()
   return
  if http_auth[0:6] != 'Basic ':
   self.set_failed()
   return
  self.login, self.password = base64.b64decode(bytes(http_auth[6:], 'ascii')).decode('ascii').split(':')
  self.fetched = True

 def set_failed(self):
  print('Status: 401 Forbidden')
  self.failed = True
 def set_failed_and_die(self):
  self.set_failed()
  print('')
  try:
   print(open(self.failfile).read())
  except:
   print('Permission denied.')
  sys.exit(0)
