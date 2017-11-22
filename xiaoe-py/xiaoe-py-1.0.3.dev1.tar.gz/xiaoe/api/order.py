from xiaoe.type import OrderQueryData, OrderCreateData, OrderUpdateData


class Order(object):
    @classmethod
    def query(cls, order_query_data: OrderQueryData, poster):
        """
        :return:
        id	string	资源id
        order_id	string	订单id
        user_id	string	用户id
        price	int	价格，单位为分
        title	string	资源名
        order_state	int	订单状态：0-未支付 1-支付成功 2-支付失败
        payment_type	int	2-单笔，3-订阅付费产品包
        out_order_id	string	外部订单
        resource_type	int	0-无（产品包），1-图文，2-音频，3-视频
        agent	string	用户下单时所用的设备信息
        created_at	string	订单时间
        """
        path = '/order.list.get/'
        return poster.post(path, order_query_data.data)

    @classmethod
    def create(cls, order_create_data: OrderCreateData, poster):
        """
        order_id	string	订单id
        price	string	价格（单位分）
        user_id	string	用户id
        purchase_name	string	商品名称
        created_at	string	订单注册时间
        """
        path = '/orders.create/'
        return poster.post(path, order_create_data.data)

    @classmethod
    def update(cls, order_update_data: OrderUpdateData, poster):
        """
        order_state	string	支付结果，1为成功，2为失败
        order_id	string	订单id
        """
        path = '/orders.state.update/'
        return poster.post(path, order_update_data.data)
