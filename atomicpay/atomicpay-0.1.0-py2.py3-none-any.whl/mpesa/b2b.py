from atomicpay.mpesa import routes
from atomicpay.mpesa import api


class B2B(object):
    def __init__(self, client):
        self.client = client

    def payment_request(self, command, to, amount,
                        reference, remarks, **kwargs):

        callback = kwargs.pop("callback", None)

        data = {
            "Initiator": self.client.configs['Initiator'],
            "SecurityCredential": self.client.configs['SecurityCredential'],
            "CommandID": command,
            "SenderIdentifierType": 4,
            "RecieverIdentifierType": 4,
            "Amount": amount,
            "PartyA": self.client.configs['Shortcode'],
            "PartyB": to,
            "AccountReference": reference,
            "Remarks": remarks,
            "QueueTimeOutURL":  kwargs.get('timeout') or self.client.configs['URLS']['B2B']['QueueTimeOutURL'],
            "ResultURL": kwargs.get('result') or self.client.configs['URLS']['B2B']['ResultURL'],
        }

        return api.call(
            route=routes.B2BPaymentRequest,
            data=data,
            access_token=self.client.auth.access_token,
            live=self.client.live,
            callback=callback
        )

    def buy_goods(self, to, amount, reference, remarks, **kwargs):

        return self.payment_request(
            "BusinessBuyGoods",
            to,
            amount,
            reference=reference,
            remarks=remarks,
            **kwargs
        )

    def paybill(self, to, amount, reference, remarks, **kwargs):

        return self.payment_request(
            "BusinessPayBill",
            to,
            amount,
            reference=reference,
            remarks=remarks,
            **kwargs
        )
