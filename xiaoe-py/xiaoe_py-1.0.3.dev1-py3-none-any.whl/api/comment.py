from xiaoe.type import CommentQueryData, CommentCreateDate


class Comment(object):
    @classmethod
    def query(cls, query_data: CommentQueryData, poster):
        """
        id	int	评论id
        content	string	评论内容
        user_id	string	发评论人的用户id
        nick_name	string	发评论人的用户昵称
        avatar	string	发评论人的头像
        src_content	string	被回复评论的内容，回复评论才返回这个字段
        src_nick_name	string	被回复人的昵称，回复评论才返回这个字段
        praise_num	int	评论的点赞数
        is_praised	int	当前访问用户是否已对该评论点赞，如果请求参数有user_id则返回该字段
        :param query_data:
        """
        path = '/comment.all.get/'
        return poster.post(path, query_data.data)

    @classmethod
    def create(cls, data: CommentCreateDate, poster):
        """
        comment_id	int	评论id
        """
        path = '/comment.add/'
        return poster.post(path, data.data)
