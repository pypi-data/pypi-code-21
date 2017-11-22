from .base import *


class BannerQueryData(BaseData):
    def __init__(self, num=None):
        self.data = OptionalDict()
        self.data['num'] = num
