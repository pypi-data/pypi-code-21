from whatap.util.date_util import DateUtil


class KeyGen(object):
    @classmethod
    def next(cls):
        return DateUtil.nowSystem()
