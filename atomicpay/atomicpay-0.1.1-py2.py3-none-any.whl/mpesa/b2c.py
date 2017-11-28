from atomicpay.mpesa import routes
from atomicpay.mpesa import api


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


class B2C(object):
    """Transfer Money From ShortCode to Phone Number

    Attributes:
        client: The mpesa client contains the auth credentials and live status
    Reference:
        https://developer.safaricom.co.ke/b2c/apis
    """

    def __init__(self, client):
        self.client = client

    def payment_request(self, command, phone, amount,
                        remarks=None, occassion=None, **kwargs):

        callback = kwargs.pop("callback", None)

        data = {
            "InitiatorName": self.client.configs['Initiator'],
            "SecurityCredential": self.client.configs['SecurityCredential'],
            "CommandID": command,
            "Amount": amount,
            "PartyA": self.client.configs['Shortcode'],
            "PartyB": phone,
            "Remarks": remarks,
            "QueueTimeOutURL":  kwargs.get('timeout') or self.client.configs['URLS']['B2C']['QueueTimeOutURL'],
            "ResultURL": kwargs.get('result') or self.client.configs['URLS']['B2C']['ResultURL'],
            "Occassion": occassion
        }

        return api.call(
            route=routes.B2CPaymentRequest,
            data=data,
            access_token=self.client.auth.access_token,
            live=self.client.live,
            callback=callback
        )

    def pay_salary(self, phone, amount, remarks, **kwargs):

        return self.payment_request(
            "SalaryPayment",
            phone,
            amount,
            remarks=remarks,
            **kwargs
        )

    def pay_business(self, phone, amount, remarks, **kwargs):
        return self.payment_request(
            "BusinessPayment",
            phone,
            amount,
            remarks=remarks,
            **kwargs
        )

    def pay_promotion(self, phone, amount, remarks, occassion, **kwargs):
        return self.payment_request(
            "PromotionPayment",
            phone,
            amount,
            remarks=remarks,
            ocassion=occassion,
            **kwargs
        )
