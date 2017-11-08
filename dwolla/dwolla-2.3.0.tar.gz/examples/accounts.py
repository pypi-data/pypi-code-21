'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the account endpoints.
'''

from dwolla import accounts, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"

# Example 1: Get basic information for a user via
# their Dwolla ID

print(accounts.basic('812-202-3784'))
# Return: {u'Latitude': 0, u'Id': u'812-202-3784', u'Longitude': 0, u'Name': u'David Stancu'}


# Example 2: Get full account information for
# the user associated with the current OAuth token

print(accounts.full())
# Return: 
# {u'City': u'New York', u'Name': u'David Stancu', u'Longitude': 0, u'State': u'NY', u'Latitude': 0, u'Type': u'Personal', u'Id': u'812-202-3784'}


# Example 3: Get the balance of the account for
# the user associated with the current OAuth token

print(accounts.balance())
# Return:
# 21.97


# Example 4: Get users near a certain geographical
# location

print(accounts.nearby(40.7127, 74.0059))
# Return:
# [{
#     "Id": "812-687-7049",
#     "Image": "https://www.dwolla.com/avatars/812-687-7049",
#     "Name": "Gordon Zheng",
#     "Latitude": 40.708448,
#     "Longitude": -74.014429,
#     "Delta": 114.72287700000001
# }]


# Example 5: Get the auto-withdrawal status of the user
# associated with the current OAuth token.

print(accounts.autowithdrawalstatus())
# Return:
# {u'Enabled': False, u'FundingId': u''}


# Example 6: Toggle the auto-withdrawal status of an account
# under the Dwolla user associated with the current OAuth token.

print(accounts.toggleautowithdrawalstatus(True, '12345678'))
# Return:
# "Enabled"