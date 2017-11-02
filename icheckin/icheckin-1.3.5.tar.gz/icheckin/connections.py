import requests
from icheckin import constants

def update_status():
   ''' 
   -< True  : Version is test; no update needed
   -> False : Check for update failed
   -> str   : Latest version to update to
   '''
   try:
      r = requests.get(constants.UPDATES, timeout=5)
   except (requests.ConnectionError, requests.ConnectTimeout, 
      requests.ReadTimeout):
      return False
   else:
      latestVersion = r.json()['latest_version']
      if constants.VERSION == latestVersion:
         return True
      else:
         return latestVersion

def checkin(cred, code):
   '''
   -> 0: Successful check-in
   -> 1: No internet connection
   -> 2: Invalid credentials
   -> 3: Not connected to SunwayEdu Wi-Fi
   -> 4: Invalid code
   -> 5: Wrong class
   -> 6: Already checked-in
   '''
   # Start a session
   session = requests.Session()
   # Login to iZone
   payload = {
      'form_action': 'submitted',
      'student_uid': cred[0],
      'password': cred[1],
   }
   try:
      r = session.post(constants.LOGIN, data=payload)
   except requests.ConnectionError:
      return 1
   if not r.history:
      return 2
   # Check for SunwayEdu Wi-Fi
   try:
      r = requests.get(constants.WIFI, timeout=2)
   except requests.ConnectTimeout:
      return 3
   except requests.ConnectionError:
      return 1
   # Check-in with code
   try:
      r = session.post(constants.CHECKIN, data={'checkin_code': code}, 
         timeout=2)
   except (requests.ReadTimeout, requests.ConnectionError):
      return 1
   if 'Checkin code not valid.' in r.text or \
      'The specified URL cannot be found.' in r.text:
      return 4
   if 'You cannot check in to a class you are not a part of.' in r.text:
      return 5
   if 'You have already checked in' in r.text:
      return 6
   return 0