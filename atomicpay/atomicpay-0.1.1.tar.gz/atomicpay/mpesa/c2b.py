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

from atomicpay.mpesa import api
from atomicpay.mpesa import routes
from atomicpay.mpesa import exceptions


class C2B(object):
    """Transfer Money From Phone Number to ShortCode

    Attributes:
        client: The mpesa client contains the auth credentials and live status    
    Reference:
        https://developer.safaricom.co.ke/c2b/apis
    """

    def __init__(self, client):
        self.client = client

    def register(self, confirmation, validation, response_type):
        """
        Register validation and confirmation URLs on M-Pesa 
        params:
        validation: Validation Url
        confirmation: Confirmation Url
        """

        data = {
            "ConfirmationURL": confirmation,
            "ResponseType": response_type,
            "ShortCode": self.client.configs['Shortcode'],
            "ValidationURL": validation
        }

        return api.call(
            route=routes.C2BRegister,
            data=data,
            access_token=self.client.auth.access_token,
            live=self.client.live
        )

    def simulate(self, command, phone, amount, reference, **kwargs):
        """Simulate a C2B txns

        """
        callback = kwargs.pop("callback", None)

        data = {
            "Amount": amount,
            "BillRefNumber": reference,
            "CommandID": command,
            "Msisdn": phone,
            "ShortCode": self.client.configs['Shortcode']
        }

        return api.call(
            route=routes.C2BSimulate,
            data=data,
            access_token=self.client.auth.access_token,
            live=self.client.live,
            callback=callback
        )

    def buy_goods(self, phone, amount, reference, **kwargs):
        """Simulate a buy good txn"""
        return self.simulate("CustomerBuyGoodsOnline", phone, amount, reference, **kwargs)

    def paybill(self, phone, amount, reference, **kwargs):
        """Simulate a paybill txn"""
        return self.simulate("CustomerPayBillOnline", phone, amount, reference, **kwargs)
