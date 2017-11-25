from atomicpay.mpesa import api
from atomicpay.mpesa import routes
from atomicpay.mpesa import exceptions


class C2B(object):

    def __init__(self, client):
        self.client = client

    def register(self, confirmation, validation, response_type):
        """
        params:
        validation: Validation Url callback
        confirmation: Confirmation Url callback
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

    def simulate(self, command, phone, amount, bill_ref, **kwargs):
        
        callback = kwargs.pop("callback", None)
        
        data = {
            "Amount": amount,
            "BillRefNumber": bill_ref,
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

    def buy_goods(self, phone, amount, ref, **kwargs):
        return self.simulate("CustomerBuyGoodsOnline", phone, amount, ref, **kwargs)

    def paybill(self, phone, amount, ref, **kwargs):
        return self.simulate("CustomerPayBillOnline", phone, amount, ref, **kwargs)
