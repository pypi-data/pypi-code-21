from os.path import join, expanduser

# Version
VERSION = '1.3.5'
# URLs
UPDATES = 'http://chunkhang.pythonanywhere.com/icheckin/api'
LOGIN = 'https://izone.sunway.edu.my/login'
WIFI = 'https://icheckin.sunway.edu.my/otp/CheckIn/isAlive/' +\
	'CuNv9UV2rXg4WtAsXUPNptg6gWQTZ52w'
CHECKIN = 'https://izone.sunway.edu.my/icheckin/iCheckinNowWithCode'
# Credentials
PATH = join(expanduser("~"), '.icheckin-credentials')
MAX = 20