'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the transaction endpoints.
'''

from dwolla import transactions, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Send $5.50 to a Dwolla ID.

print(transactions.send('812-197-4121', 5.50))
# Return:
# 113533 (Sender's transaction ID)


# Example 2: List transactions for the user
# associated with the current OAuth token.

print(transactions.get())
# Return:
# [
#     {
#         "Id": 113533,
#         "Amount": 5.50,
#         "Date": "2014-12-13T05:07:15Z",
#         "Type": "money_sent",
#         "UserType": "Email",
#         "DestinationId": "812-197-4121",
#         "DestinationName": "Some Name",
#         "Destination": {
#             "Id": "812-197-4121",
#             "Name": "Some Name",
#             "Type": "dwolla",
#             "Image": ""
#         },
#         "SourceId": "812-202-3784",
#         "SourceName": "David Stancu",
#         "Source": {
#             "Id": "812-202-3784",
#             "Name": "David Stancu",
#             "Type": "Dwolla",
#             "Image": "https://dwolla-avatars.s3.amazonaws.com/812-202-3784/ac045522"
#         },
#         "ClearingDate": "",
#         "Status": "cancelled",
#         "Notes": "",
#         "Fees": null,
#         "OriginalTransactionId": null,
#         "Metadata": null
#     },
#     ...
# ]

# Example 3: Refund $2 from "Balance" from transaction
# '123456'

print(transactions.refund('3452346', 'Balance', 2.00))
# Return:
# {
#     "TransactionId": 4532,
#     "RefundDate": "2014-12-10T12:01:09Z",
#     "Amount": 2.00
# }


# Example 4: Get info for transaction ID '123456'.

print(transactions.info('113533'))
# Return:
#     {
#         "Id": 113533,
#         "Amount": 5.50,
#         "Date": "2014-12-13T05:07:15Z",
#         "Type": "money_sent",
#         "UserType": "Email",
#         "DestinationId": "812-197-4121",
#         "DestinationName": "Some Name",
#         "Destination": {
#             "Id": "812-197-4121",
#             "Name": "Some Name",
#             "Type": "dwolla",
#             "Image": ""
#         },
#         "SourceId": "812-202-3784",
#         "SourceName": "David Stancu",
#         "Source": {
#             "Id": "812-202-3784",
#             "Name": "David Stancu",
#             "Type": "Dwolla",
#             "Image": "https://dwolla-avatars.s3.amazonaws.com/812-202-3784/ac045522"
#         },
#         "ClearingDate": "",
#         "Status": "cancelled",
#         "Notes": "",
#         "Fees": null,
#         "OriginalTransactionId": null,
#         "Metadata": null
#     }


# Example 5: Get transaction statistics for the user
# associated with the current OAuth token.

print(transactions.stats())
# Return:
# {
#     "TransactionsCount": 5,
#     "TransactionsTotal": 116.92
# }

# Example 6: Schedule a transaction for 2018-01-01 with
# amount $5.50

print(transactions.schedule('812-111-1111', 5.50, '2018-01-01', '5da016f7769bcc1de9998a30d194d5a7'))
# Return: 
#     "Id": "3bfaf7fb-b5e9-4a6e-ab09-1ef30d30bbef",
#     "ScheduledDate": "2018-01-01",
#     "ExpectedClearingDate": "2018-01-06",
#     "TransactionId": null,
#     "Amount": 5.50,
#     "FundingSource": "5da016f7769bcc1de9998a30d194d5a7",
#     "AssumeCosts": false,
#     "Destination": {
#         "Id": "812-111-1111",
#         "Name": "Jane Doe",
#         "Type": "Dwolla",
#         "Image": "http://www.dwolla.com/avatars/812-111-1111"
#     },
#     "Status": "scheduled",
#     "CreatedDate": "2014-09-12T20:37:37Z",
#     "Metadata": {
#       "foo": "bar"
#     }

# Example 7: Get all scheduled transactions
print(transactions.scheduled())
# Return: List of scheduled transactions
#[
#     "Id": "asr3r34t",
#     "ScheduledDate": "2018-01-01",
#     "ExpectedClearingDate": "2018-01-06",
#     "TransactionId": null,
#     "Amount": 10.50,
#     "FundingSource": "5da016f7769bcc1de9998a30d194d5a7",
#     "AssumeCosts": false,
#     "Destination": {
#         "Id": "812-111-1111",
#         "Name": "Jane Doe",
#         "Type": "Dwolla",
#         "Image": "http://www.dwolla.com/avatars/812-111-1111"
#     },
#     "Status": "scheduled",
#     "CreatedDate": "2014-09-12T20:37:37Z",
#     "Metadata": {
#       "foo": "bar"
#     }
# ...
#]

# Example 8: Get scheduled transaction with 
# ID 'asbfdjk434'
print transactions.scheduledbyid('asbfdjk434')


# Example 9: Edit scheduled transaction with ID
# 'asr3r34t' to reflect amount 10.50
print transactions.editscheduledbyid('asr3r34t', {'amount': 10.50})
# Return: 
#     "Id": "asr3r34t",
#     "ScheduledDate": "2018-01-01",
#     "ExpectedClearingDate": "2018-01-06",
#     "TransactionId": null,
#     "Amount": 10.50,
#     "FundingSource": "5da016f7769bcc1de9998a30d194d5a7",
#     "AssumeCosts": false,
#     "Destination": {
#         "Id": "812-111-1111",
#         "Name": "Jane Doe",
#         "Type": "Dwolla",
#         "Image": "http://www.dwolla.com/avatars/812-111-1111"
#     },
#     "Status": "scheduled",
#     "CreatedDate": "2014-09-12T20:37:37Z",
#     "Metadata": {
#       "foo": "bar"
#     }

# Example 10: Delete scheduled transaction with ID
# 'id to delete'
print transactions.deletescheduledbyid('id to delete')
# Return: "id to delete"

# Example 11: Delete all scheduled transactions
print transactions.deleteallscheduled()
# Return
# ['deleted id 1', 'deleted id 2', 'deleted id 3']
