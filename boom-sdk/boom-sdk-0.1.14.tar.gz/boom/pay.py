import os

from boom.api import API


class PayService(API):

    def __init__(self):
        self.url = os.getenv("BOOM_PAY_URL", "https://pay.boomletsgo.com")


class PayResponse(object):

    def __init__(self):
        self.pay = None
