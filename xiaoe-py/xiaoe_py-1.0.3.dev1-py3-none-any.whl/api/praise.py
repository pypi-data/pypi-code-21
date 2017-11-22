from xiaoe.type import PraiseOperateData


class Praise(object):
    @classmethod
    def operate(cls, data: PraiseOperateData, poster):
        path = '/praise.add/'
        return poster.post(path, data.data)
