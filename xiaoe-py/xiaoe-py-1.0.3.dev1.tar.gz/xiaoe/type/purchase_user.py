from .base import BaseData, OptionalDict


class PurchaseUserQueryData(BaseData):
    """
    payment_type	是	string	产品类型：2-单笔（单个商品）、3-付费产品包（专栏会员等）
    resource_type	是	string	单笔时为必要参数，资源类型：1-图文、2-音频、3-视频、4-直播、5-活动报名、7-社群
    resource_id	是	string	单笔时为必要参数，资源id
    product_id	是	string	产品包时为必要参数，产品包id
    page_index	否	string	页码，从0开始 ，默认为0
    page_size	否	string	每页请求条数，最大支持300，默认取10条
    order_by	否	string	排序方式。格式为column:asc/desc，column可选值：created_at 创建时间/updated_at 更新时间，默认为created_at:desc
    """
    def __init__(self, payment_type=None, resource_type=None, resource_id=None,
                 product_id=None, page_index=None, page_size=None, order_by=None):
        self.data = OptionalDict()
        self.data['payment_type'] = payment_type
        self.data['resource_type'] = resource_type
        self.data['resource_id'] = resource_id
        self.data['product_id'] = product_id
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['order_by'] = order_by
