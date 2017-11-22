from xiaoe.type import PurchaseUserQueryData


class PurchaseUser(object):
    @classmethod
    def query(cls, data: PurchaseUserQueryData, poster):
        """
        img_url	string	产品图
        purchase_name	string	产品名
        res_id	string	产品id
        user_id	string	用户id
        nickname	string	用户昵称
        avatar	string	用户头像
        union_id	string	用户的union_id
        phone	string	用户手机
        account_type	string	用户类型 0-微信，10-开放平台
        """
        path = '/purchase.userslist.get/'
        return poster.post(path, data.data)
