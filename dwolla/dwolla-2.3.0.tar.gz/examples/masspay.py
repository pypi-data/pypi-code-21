'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the masspay endpoints.
'''

from dwolla import masspay, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Create a MassPay job with two items to
# the Balance of the user associated with the current
# OAuth token.

info = masspay.create('Balance',
               {
                   {
                       'amount': 1.00,
                       'destination': '812-197-4121'
                   },
                   {
                       'amount': 2.00,
                       'destination': '812-174-9528'
                   }
               })

print(info)
# Return: 
# {
#         "Id": "47fe2f7c-8d6d-4f98-bcd9-a3100178062f",
#         "AssumeCosts": true,
#         "FundingSource": "Balance",
#         "Total": 3.00,
#         "Fees": 0,
#         "CreatedDate": "2014-04-18T05:49:03Z",
#         "Status": "queued",
#         "ItemSummary": {
#             "Count": 2,
#             "Completed": 0,
#             "Successful": 0
# }


# Example 2: Get info regarding the MassPay
# job which you have just created.

print(masspay.getjob(info['Id']))
# Return: 
# {
#         "Id": "47fe2f7c-8d6d-4f98-bcd9-a3100178062f",
#         "AssumeCosts": true,
#         "FundingSource": "Balance",
#         "Total": 3.00,
#         "Fees": 0,
#         "CreatedDate": "2014-04-18T05:49:03Z",
#         "Status": "complete",
#         "ItemSummary": {
#             "Count": 2,
#             "Completed": 2,
#             "Successful": 2
# }


# Example 3: Get all the items submitted with the
# MassPay job which you have just created.

items = masspay.getjobitems(info['Id'])
print(items)
# Return:
# [
#         {
#             "JobId": "643f2db9-5b45-4755-a881-a3100178b6d7",
#             "ItemId": 13,
#             "Destination": "812-197-4121",
#             "DestinationType": "dwolla",
#             "Amount": 1.00,
#             "Status": "success",
#             "TransactionId": 4938766,
#             "Error": null,
#             "CreatedDate": "2014-04-18T05:51:34Z"
#         },
#         {
#             "JobId": "643f2db9-5b45-4755-a881-a3100178b6d7",
#             "ItemId": 14,
#             "Destination": "812-174-9528",
#             "DestinationType": "dwolla",
#             "Amount": 2.00,
#             "Status": "success",
#             "TransactionId": 4938768,
#             "Error": null,
#             "CreatedDate": "2014-04-18T05:51:34Z",
#             "Metadata": null 
#         }
# ]


# Example 4: Get information about the 0th item from
# the MassPay job you just submitted.
#
# Note: You do not need to get all items first, I just
# re-use data for illustrative purposes.

print(masspay.getitem(info['Id'], items[0]['ItemId']))
# Return: 
# {
#     "JobId": "643f2db9-5b45-4755-a881-a3100178b6d7",
#     "ItemId": 13,
#     "Destination": "812-197-4121",
#     "DestinationType": "dwolla",
#     "Amount": 1.00,
#     "Status": "success",
#     "TransactionId": 4938766,
#     "Error": null,
#     "CreatedDate": "2014-04-18T05:51:34Z"
# }


# Example 5: Get all current MassPay jobs for the
# user associated with the current OAuth token.

print(masspay.listjobs())
# Return:
# [
#         {
#             "Id": "643f2db9-5b45-4755-a881-a3100178b6d7",
#             "UserJobId": "I've got a job for ya",
#             "AssumeCosts": true,
#             "FundingSource": "Balance",
#             "Total": 0.02,
#             "Fees": 0,
#             "CreatedDate": "2014-04-18T05:51:34Z",
#             "Status": "complete",
#             "ItemSummary": {
#                 "Count": 2,
#                 "Completed": 2,
#                 "Successful": 2
#             }
#         },
#         {
#             "Id": "634de23d-ab50-4a53-bcd2-a310017794a8",
#             "UserJobId": "I've got another job for ya",
#             "AssumeCosts": true,
#             "FundingSource": "Balance",
#             "Total": 2,
#             "Fees": 0,
#             "CreatedDate": "2014-04-18T05:47:26Z",
#             "Status": "complete",
#             "ItemSummary": {
#                 "Count": 2,
#                 "Completed": 2,
#                 "Successful": 2
#             }
#         }
# ]