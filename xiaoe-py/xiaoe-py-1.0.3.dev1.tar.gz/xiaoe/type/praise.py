from .base import BaseData, OptionalDict


class PraiseOperateData(BaseData):
    """
    user_id	是	string	点赞用户id
    comment_id	是	string	被点赞的评论
    record_id	是	string	点赞所属的资源id
    operate_type	是	int	操作类型 0-取消点赞 1-点赞
    """
    def __init__(self, user_id=None, comment_id=None, record_id=None, operate_type=None):
        self.data = OptionalDict()
        self.data['user_id'] = user_id
        self.data['comment_id'] = comment_id
        self.data['record_id'] = record_id
        self.data['operate_type'] = operate_type
