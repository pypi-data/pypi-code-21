# Copyright (c) 2017 Turbopay Holdings Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# Sandbox base url
SANBOX_BASE_URL = "https://sandbox.safaricom.co.ke/"

# Live base url
LIVE_BASE_URL = "https://api.safaricom.co.ke/"

# Mpesa Txn Reversal
Reverse = "mpesa/reversal/v1/request"

# B2C Payment Request
B2CPaymentRequest = "mpesa/b2c/v1/paymentrequest"

# Mpesa Account Balance
AccountBalance = "mpesa/accountbalance/v1/query"

# Transaction Status
TransactionStatus = "mpesa/transactionstatus/v1/query"

# B2B Payment Request
B2BPaymentRequest = "mpesa/b2b/v1/paymentrequest"

# Lipa Na M-Pesa Query Request API
LNMQueryRequest = "mpesa/stkpushquery/v1/query"

# Lipa Na M-Pesa Online Payment API
LNMOnlinePayment = "mpesa/stkpush/v1/processrequest"

# Generate Token
Token = "oauth/v1/generate?grant_type=client_credentials"

# C2B Register URL
C2BRegister = "mpesa/c2b/v1/registerurl"

# C2B Simulate Transaction
C2BSimulate = "mpesa/c2b/v1/simulate"
