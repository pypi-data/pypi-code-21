from xiaoe.type import PurchaserQueryData, PurchaserDeleteData


class Purchase(object):
    @classmethod
    def query(cls, data: PurchaserQueryData, poster):
        """
        id	string	资源id （资源是单品，id为资源id，资源是产品包，id为产品包id）
        price	int	价格，单位为分
        title	string	资源名
        payment_type	int	2-单笔，3-订阅付费产品包
        resource_type	int	0-无（产品包），1-图文，2-音频，3-视频
        is_member	int	会员标识（单品不返回该字段，该专栏是否兼做会员 0-否 1-是）
        recent_resource	string	专栏或会员最新更新资源名称
        agent	string	用户购买时所用的设备信息
        """
        path = '/purchase.list.get/'
        return poster.post(path, data.data)

    @classmethod
    def delete(cls, data: PurchaserDeleteData, poster):
        """
        delete	int	1订阅取消成功
        """
        path = '/purchase.delete/'
        return poster.post(path, data.data)
