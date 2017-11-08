'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the request endpoints.
'''

from dwolla import request, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Request $5 from 812-740-3809

print(request.create('812-740-3809', 5.00))
# Return:
# 1470 (request ID)


# Example 2: Get all pending requests from the user
# associated with the current OAuth token.
print(request.get())
# Return:
# [
#         {
#             "Id": 640,
#             "Source": {
#                 "Id": "812-693-9484",
#                 "Name": "Spencer Hunter",
#                 "Type": "Dwolla",
#                 "Image": null
#             },
#             "Destination": {
#                 "Id": "812-706-1396",
#                 "Name": "Jane Doe",
#                 "Type": "Dwolla",
#                 "Image": null
#             },
#             "Amount": 5.00,
#             "Notes": "",
#             "DateRequested": "2014-07-23T21:49:06Z",
#             "Status": "Pending" ,
#             "Transaction": null,
#             "CancelledBy": null,
#             "DateCancelled": "",
#             "SenderAssumeFee": false,
#             "SenderAssumeAdditionalFees": false,
#             "AdditionalFees": [],
#             "Metadata": null 
#         },
#         ...
# ]


# Example 3: Get info regarding a pending money request.
print(request.info(1470))
# Return:
#         {
#             "Id": 1470,
#             "Source": {
#                 "Id": "812-693-9484",
#                 "Name": "Spencer Hunter",
#                 "Type": "Dwolla",
#                 "Image": null
#             },
#             "Destination": {
#                 "Id": "812-706-1396",
#                 "Name": "Jane Doe",
#                 "Type": "Dwolla",
#                 "Image": null
#             },
#             "Amount": 5.00,
#             "Notes": "",
#             "DateRequested": "2014-07-23T21:49:06Z",
#             "Status": "Pending" ,
#             "Transaction": null,
#             "CancelledBy": null,
#             "DateCancelled": "",
#             "SenderAssumeFee": false,
#             "SenderAssumeAdditionalFees": false,
#             "AdditionalFees": [],
#             "Metadata": null 
#         }


# Example 4: Cancel a pending money request.

print(request.cancel(1470))
# Return:
# Empty string if successful, error will be raised if not.


# Example 5: Fulfill a pending money request.

print(request.fulfill(1475, 10.00))
# Return:
# {
#         "Id": 147659,
#         "RequestId": 1475,
#         "Amount": 10.00,
#         "SentDate": "2014-01-22T13:11:10Z",
#         "ClearingDate": "2014-01-22T13:11:10Z",
#         "Status": "processed" ,
#         "Source": {
#             "Id": "812-693-9484",
#             "Name": "Michael Schonfeld",
#             "Type": "Dwolla",
#             "Image": null
#         },
#         "Destination": {
#             "Id": "812-600-6705",
#             "Name": "Michael Schonfeld",
#             "Type": "Dwolla",
#             "Image": null
#         }
# }