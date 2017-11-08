'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the contacts endpoints.
'''

from dwolla import contacts, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Get the first 10 contacts from the user
# associated with the current OAuth token.

print(contacts.get())
# Return:
# [{u'City': u'Des Moines', u'Name': u'Dwolla, Inc.', u'Image': u'https://www.dwolla.com/avatars/812-616-9409', u'State': u'IA', u'Type': u'Dwolla', u'Id': u'812-616-9409'}, 
# {u'City': u'Elmhurst', u'Name': u'Gordon Zheng', u'Image': u'https://www.dwolla.com/avatars/812-687-7049', u'State': u'NY', u'Type': u'Dwolla', u'Id': u'812-687-7049'}]


# Example 2: Get the first 2 contacts from the user
# associated with the current OAuth token.

print(contacts.get(limit=2))
# Return: 
# Same as above (David has only two contacts)


# Example 3: Get Dwolla spots near NYC's official
# coordinates.

print(contacts.nearby(40.7127, 74.0059))
# Return:
# [
#        {
#            "Name": "ThelmasTreats",
#            "Id": "812-608-8758",
#            "Type": "Dwolla",
#            "Image": "https://www.dwolla.com/avatars/812-608-8758",
#            "Latitude": 41.590043,
#            "Longitude": -93.62095,
#            "Address": "615 3rd Street\n",
#            "City": "Des Moines",
#            "State": "IA",
#            "PostalCode": "50309",
#            "Group": "812-608-8758",
#            "Delta": 0.0009069999999908873
#        },
#        {
#            "Name": "IKONIX Studio",
#            "Id": "812-505-4939",
#            "Type": "Dwolla",
#            "Image": "https://www.dwolla.com/avatars/812-505-4939",
#            "Latitude": 41.5887958,
#            "Longitude": -93.6215057,
#            "Address": "506 3rd St\nSuite 206",
#            "City": "Des Moines",
#            "State": "IA",
#            "PostalCode": "50309",
#            "Group": "812-505-4939",
#            "Delta": 0.0027098999999992657
#        }
# ]
