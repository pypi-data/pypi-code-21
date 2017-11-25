import requests
from functools import wraps

from atomicpay.mpesa.b2b import B2B
from atomicpay.mpesa.b2c import B2C
from atomicpay.mpesa.c2b import C2B
from atomicpay.mpesa.lipa import Lipa

from atomicpay.mpesa import api
from atomicpay.mpesa.auth import Auth
from atomicpay.mpesa import exceptions
from atomicpay.mpesa import routes


class Mpesa(object):
    """Mpesa Client"""

    def __init__(self, key, secret, config, live=False):

        if not isinstance(config, dict):
            msg = "Expected config to be of type dict got type {}".format(type(config))
            raise exceptions.AuthTypeError(msg)

        self.live = live
        self.configs = config
        self.auth = Auth(key, secret, live)

    def balance(self, remarks=None, **kwargs):

        msg = "Account balance" if remarks is None else remarks
        callback = kwargs.pop("callback", None)

        data = {
            "Initiator": self.configs['Initiator'],
            "SecurityCredential": self.configs['SecurityCredential'],
            "CommandID": "AccountBalance",
            "PartyA": self.configs['Shortcode'],
            "IdentifierType": "4",
            "Remarks": msg,
            "QueueTimeOutURL": kwargs.get('timeout') or self.configs['URLS']['BALANCE']['QueueTimeOutURL'],
            "ResultURL": kwargs.get('result') or self.configs['URLS']['BALANCE']['ResultURL'],
            **kwargs
        }
        return api.call(
            access_token=self.auth.access_token,
            route=routes.AccountBalance,
            data=data,
            live=self.live,
            callback=callback
        )

    def transaction(self, txn_id, origin_id, **kwargs):

        callback = kwargs.pop("callback", None)

        data = {
            "Initiator": self.configs['Initiator'],
            "SecurityCredential": self.configs['SecurityCredential'],
            "CommandID": "TransactionStatusQuery",
            "TransactionID": txn_id,
            "PartyA": self.configs['Shortcode'],
            "IdentifierType": "4",
            "QueueTimeOutURL": kwargs.get('timeout') or self.configs['URLS']['TRANSACTIONS']['QueueTimeOutURL'],
            "ResultURL": kwargs.get('result') or self.configs['URLS']['TRANSACTIONS']['ResultURL'],
            "Remarks": "Transaction Details",
            "Occasion": " ",
            "OriginatorConversationID": origin_id,
            **kwargs
        }

        return api.call(
            access_token=self.auth.access_token,
            route=routes.TransactionStatus,
            data=data,
            live=self.live,
            callback=callback
        )
    
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self


def define_methods(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


Mpesa.b2b = define_methods(B2B)
Mpesa.b2c = define_methods(B2C)
Mpesa.c2b = define_methods(C2B)
Mpesa.lipa = define_methods(Lipa)
