from django.conf import settings
from boxberry.exceptions import *
from boxberry.client import BoxberryAPI as OriginalBoxberryAPI


class BoxberryAPI(OriginalBoxberryAPI):
    def __init__(self, token=None, endpoint=None, request_timeout=10):
        super(BoxberryAPI, self).__init__(
            token=token or settings.BOXBERRY_TOKEN,
            endpoint=endpoint or settings.BOXBERRY_ENDPOINT,
            request_timeout=request_timeout,
        )
