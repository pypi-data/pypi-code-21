from .base import BaseData, OptionalDict


class CombineQueryData(BaseData):
    """
    cmd	是	string	命令字，可选值：column.all.get 、audio.detail.get、video.detail.get、comment.all.get、message.send 等
    order_by	否	string	排序方式。格式为column:asc/desc，column可选值：start_at 上架时间 / created_at 创建时间
    page_index	否	string	页码，从0开始
    page_size	否	string	每页请求条数，最大支持300
    user_id	否	string	用户id
    """
    def __init__(self, cmd=None, order_by=None, page_index=None, page_size=None, user_id=None):
        self.data = OptionalDict()
        self.data['cmd'] = cmd
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['user_id'] = user_id
