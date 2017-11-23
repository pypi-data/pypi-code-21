import json
import time
from ..utils import js_float, js_int


class Deal:
    def __str__(self):
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    def __init__(self, _str):
        sp = _str.split(',')
        self.symbol = sp[0]
        self.market = sp[0][:2]
        self.code = sp[0][2:]
        self.index = sp[1]
        self.timestamp = js_float(sp[2])
        self.price = js_float(sp[3])
        self.volume = js_int(sp[4])
        self.amount = js_float(sp[5])
        self.bid = sp[6]
        self.aid = sp[7]
        self.channel = sp[8]
        self.flag = sp[9]
