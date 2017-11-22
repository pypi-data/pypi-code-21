from .base import BaseData, OptionalDict


class OrderQueryData(BaseData):
    """
    order_by	否	string	排序方式。格式为column:asc/desc，column可选值：created_at 创建时间/updated_at 更新时间，默认为created_at:desc
    page_index	否	string	页码，从0开始 ,默认为0
    page_size	否	string	每页请求条数，最大支持300,默认取10条
    user_id	否	string	用户id
    begin_time	否	string	查询起始时间，unix 时间戳
    end_time	否	string	查询结束时间，unix 时间戳
    order_state	否	int	订单状态：0-未支付 1-支付成功 2-支付失败
    resource_type	否	int	查询单笔资源时(即payment_type=2时)需传入该参数，1-图文 2-音频 3-视频 不填查全部类型
    payment_type	否	int	付费类型 2-单笔、3-订阅付费产品包(专栏和会员)
    client_type	否	int	购买时使用的客户端类型，0-公众号 1-小程序 10-其他，不填查全部类型
    """
    def __init__(self, order_by=None, page_index=None, page_size=None, user_id=None,
                 begin_time=None, end_time=None, order_state=None, resource_type=None,
                 payment_type=None, client_type=None):
        self.data = OptionalDict()
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['user_id'] = user_id
        self.data['begin_time'] = begin_time
        self.data['end_time'] = end_time
        self.data['order_state'] = order_state
        self.data['resource_type'] = resource_type
        self.data['payment_type'] = payment_type
        self.data['client_type'] = client_type


class OrderCreateData(BaseData):
    """
    payment_type	是	string	购买方式：2-单笔（单个商品）、3-付费产品包（专栏会员等）
    resource_type	是	string	单笔购买时为必要参数，资源类型：1-图文、2-音频、3-视频、4-直播
    resource_id	是	string	单笔购买时为必要参数，资源id
    product_id	否	string	购买产品包时为必要参数，产品包id
    user_id	是	string	购买商品的用户id
    out_order_id	否	string	商户填入自己的订单号
    """
    def __init__(self, payment_type=None, resource_type=None, resource_id=None,
                 product_id=None, user_id=None, out_order_id=None):
        self.data = OptionalDict()
        self.data['payment_type'] = payment_type
        self.data['resource_type'] = resource_type
        self.data['resource_id'] = resource_id
        self.data['product_id'] = product_id
        self.data['user_id'] = user_id
        self.data['out_order_id'] = out_order_id


class OrderUpdateData(BaseData):
    def __init__(self, order_state=None, order_id=None):
        self.data = OptionalDict()
        self.data['order_state'] = order_state
        self.data['order_id'] = order_id
