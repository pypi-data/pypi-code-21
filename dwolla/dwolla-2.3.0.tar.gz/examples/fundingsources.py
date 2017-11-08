'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the funding-source endpoints.
'''

from dwolla import fundingsources, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Get information about a funding ID

print(fundingsources.info('12345678'))
# Return:
# {
# "Id": "12345678",
# "Name": "Donations Payout Account - Checking",
# "Type": "Checking",
# "Verified": true,
# "ProcessingType": "FiSync"
# }


# Example 2: Get a list of funding sources associated
# with the account under the current OAuth token

print(fundingsources.get())
# Return:
# [
# {
#     "Id": "Balance",
#     "Name": "My Dwolla Balance",
#     "Type": "",
#     "Verified": "true",
#     "ProcessingType": ""
# },
# {
#     "Id": "c58bb9f7f1d51d5547e1987a2833f4fa",
#     "Name": "Donations Collection Fund - Savings",
#     "Type": "Savings",
#     "Verified": "true",
#     "ProcessingType": "ACH"
# },
# {
#     "Id": "Credit",
#     "Name": "Credit",
#     "Type": "",
#     "Verified": "true",
#     "ProcessingType": ""
# },
# {
#     "Id": "c58bb9f7f1d51d5547e1987a2833f4fb",
#     "Name": "Donations Payout Account - Checking",
#     "Type": "Checking",
#     "Verified": "true",
#     "ProcessingType": "FiSync"
# }
# ]


# Example 3: Add a funding source to the account associated
# with the current OAuth token.
#
# '12345678' is the account number.
# '00000000' is the routing number.
# 'Checking' is the account type.
# 'My Bank' is a user defined account identifier string.

print(fundingsources.add('12345678', '00000000', 'Checking', 'My Bank'))
# Return:
# {
#         "Id": "34da835f235cd25302ef0c5c1cb1d4b9",
#         "Name": "My Bank",
#         "Type": "Checking",
#         "Verified": false,
#         "ProcessingType": "ACH"
# }


# Example 4: Verify the newly created account with via
# the two micro-deposits.
#
# '0.04' is the first deposit.
# '0.02' is the second deposit.
# '12345678' is the account number.

print(fundingsources.verify(0.04, 0.02, '12345678'))
# Return:
# {
#         "Id": "12345678",
#         "Name": "My Checking Account - Checking",
#         "Type": "Checking",
#         "Verified": true,
#         "ProcessingType": "ACH"
# }


# Example 5: Withdraw $5 from Dwolla to funding ID
# '12345678'.

print(fundingsources.withdraw(5.00, '12345678'))
# Return: 
# { 
#         "Id": 12345678,
#         "Amount": 5,
#         "Date": "2014-09-05T06:40:56Z",
#         "Type": "withdrawal",
#         "UserType": "Dwolla",
#         "DestinationId": "XXX9999",
#         "DestinationName": "Blah",
#         "Destination": { 
#             "Id": "XXX9999", 
#             "Name": "Blah", 
#             "Type": "Dwolla", 
#             "Image": ""
#         },
#         "SourceId": "812-742-8722",
#         "SourceName": "Cafe Kubal",
#         "Source": {
#             "Id": "812-742-8722",
#             "Name": "Cafe Kubal",
#             "Type": "Dwolla",
#             "Image": "http://uat.dwolla.com/avatars/812-742-8722" 
#         },
#         "ClearingDate": "2014-09-08T00:00:00Z",
#         "Status": "pending",
#         "Notes": null,
#         "Fees": null,
#         "OriginalTransactionId": null,
#         "Metadata": null 
#       }
# }


# Example 6: Deposit $10 into Dwolla from funding ID
# '12345678'.

print(fundingsources.deposit(10.00, '12345678'))
# Return:
# { 
#        "Id": 12345678,
#        "Amount": 5,
#        "Date": "2014-09-05T06:40:56Z",
#        "Type": "deposit",
#        "UserType": "Dwolla",
#        "DestinationId": "XXX9999",
#        "DestinationName": "Blah",
#        "Destination": {
#            "Id": "812-742-8722",
#            "Name": "Cafe Kubal",
#            "Type": "Dwolla",
#            "Image": "http://uat.dwolla.com/avatars/812-742-8722" 
#        },
#        "SourceId": "812-742-8722",
#        "SourceName": "Cafe Kubal",
#        "Source": { 
#            "Id": "XXX9999", 
#            "Name": "Blah", 
#            "Type": "Dwolla", 
#            "Image": ""
#        },
#        "ClearingDate": "2014-09-08T00:00:00Z",
#        "Status": "pending",
#        "Notes": null,
#        "Fees": null,
#        "OriginalTransactionId": null,
#        "Metadata": null 
# }