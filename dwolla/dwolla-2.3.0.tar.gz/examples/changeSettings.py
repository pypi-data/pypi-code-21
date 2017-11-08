'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for passing in your
  own settings with dwolla-python.
'''

# Import everything from the dwolla package
from dwolla import *

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"


# Example 1: Get basic information for a user via
# their Dwolla ID.

print(accounts.basic('812-202-3784'))

# Return:
# {u'Latitude': 0, u'Id': u'812-202-3784', u'Longitude': 0, u'Name': u'David Stancu'}

# Example 2: Get full account information for
# the user associated with the current OAuth token

print(contacts.get())

# Return: 
# [{u'City': u'Des Moines', u'Name': u'Dwolla, Inc.', u'Image': u'https://www.dwolla.com/avatars/812-616-9409', u'State': u'IA', u'Type': u'Dwolla', u'Id': u'812-616-9409'}, 
#  {u'City': u'Elmhurst', u'Name': u'Gordon Zheng', u'Image': u'https://www.dwolla.com/avatars/812-687-7049', u'State': u'NY', u'Type': u'Dwolla', u'Id': u'812-687-7049'}]
