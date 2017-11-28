from atomicpay.mpesa import routes
from atomicpay.mpesa import api


class B2C(object):
    def __init__(self, client):
        self.client = client

    def payment_request(self, command, to, amount,
                        remarks=None, occassion=None, **kwargs):

        callback = kwargs.pop("callback", None)

        data = {
            "InitiatorName": self.client.configs['Initiator'],
            "SecurityCredential": self.client.configs['SecurityCredential'],
            "CommandID": command,
            "Amount": amount,
            "PartyA": self.client.configs['Shortcode'],
            "PartyB": to,
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

    def pay_salary(self, to, amount, remarks, **kwargs):

        return self.payment_request(
            "SalaryPayment",
            to,
            amount,
            remarks=remarks,
            **kwargs
        )

    def pay_business(self, to, amount, remarks, **kwargs):
        return self.payment_request(
            "BusinessPayment",
            to,
            amount,
            remarks=remarks,
            **kwargs
        )

    def pay_promotion(self, to, amount, remarks, occassion, **kwargs):
        return self.payment_request(
            "PromotionPayment",
            to,
            amount,
            remarks=remarks,
            ocassion=occassion,
            **kwargs
        )
