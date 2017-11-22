from .base import BaseData, OptionalDict


class CommentQueryData(BaseData):
    """
    page_index	否	string	页码，从0开始，默认为0
    page_size	否	string	每页请求条数，最大支持300，默认取10条
    resource_id	是	string	资源id
    resource_type	是	int	资源类型 1-图文 2-音频 3-视频
    user_id	否	string	用户id
    """
    def __init__(self, page_index=None, page_size=None, resource_id=None, resource_type=None, user_id=None):
        self.data = OptionalDict()
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['resource_id'] = resource_id
        self.data['resource_type'] = resource_type
        self.data['user_id'] = user_id


class CommentCreateDate(BaseData):
    """
    user_id	是	string	发评论人的用户id
    content	是	string	评论内容
    record_id	是	string	评论所属的资源id
    resource_type	是	string	评论所属的资源类型 1-图文 2-音频 3-视频
    src_comment_id	否	string	被回复的评论id，回复评论需该字段，其他评论不需要
    src_content	否	string	被回复的评论内容，回复评论需该字段，其他评论不需要
    """
    def __init__(self, user_id=None, content=None, record_id=None, resource_type=None,
                 src_comment_id=None, src_content=None):
        self.data = OptionalDict()
        self.data['user_id'] = user_id
        self.data['content'] = content
        self.data['record_id'] = record_id
        self.data['resource_type'] = resource_type
        self.data['src_comment_id'] = src_comment_id
        self.data['src_content'] = src_content

