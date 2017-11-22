from xiaoe.type import CombineQueryData


class Combine(object):

    @classmethod
    def query(cls, data: CombineQueryData, poster):
        """
        :return:
        price	int	价格,单位为分
        is_available	int	请求参数中user_id对应的用户是否购买了该资源 ，0-未购买 1-已购买，如未传入user_id,则不返回该字段
        state	int	资源状态， 0-可见 1-隐藏 2-删除
        view_count	int	资源浏览量
        comment_count	int	资源评论数
        """
        path = '/combine/'
        return poster.post(path, data.data)
