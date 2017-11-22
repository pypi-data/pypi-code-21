from functools import partial

from .api.banner import Banner
from .api.column import Column
from .api.resource import Resource
from .api.combine import Combine
from .api.comment import Comment
from .api.message import Message
from .api.order import Order
from .api.praise import Praise
from .api.purchase import Purchase
from .api.purchase_user import PurchaseUser
from .api.user import User
from .post import Poster
from .type import *


class XiaoESDK(Poster, object):
    """
    小鹅通sdk 的 python package
    https://api-doc.xiaoe-tech.com/index.php
    """
    def __init__(self, appid, secret, version='1.0'):
        super(XiaoESDK, self).__init__(appid, secret, version=version)

        self.banner = Banner
        self.banner.query = partial(self.banner.query, poster=self)

        self.column = Column
        self.column.detail = partial(self.column.detail, poster=self)
        self.column.query = partial(self.column.query, poster=self)
        self.column.query_have_role = partial(self.column.query_have_role, poster=self)

        self.combine = Combine
        self.combine.query = partial(self.combine.query, poster=self)

        self.comment = Comment
        self.comment.create = partial(self.comment.create, poster=self)
        self.comment.query = partial(self.comment.query, poster=self)

        self.message = Message
        self.message.create = partial(self.message.create, poster=self)

        self.order = Order
        self.order.create = partial(self.order.create, poster=self)
        self.order.query = partial(self.order.query, poster=self)
        self.order.update = partial(self.order.update, poster=self)

        self.praise = Praise
        self.praise.operate = partial(self.praise.operate, poster=self)

        self.purchase = Purchase
        self.purchase.delete = partial(self.purchase.delete, poster=self)
        self.purchase.query = partial(self.purchase.query, poster=self)

        self.purchaseuser = PurchaseUser
        self.purchaseuser.query = partial(self.purchaseuser.query, poster=self)

        self.resource = Resource
        self.resource.audio_detail = partial(self.resource.audio_detail, poster=self)
        self.resource.imagetext_detail = partial(self.resource.imagetext_detail, poster=self)
        self.resource.query = partial(self.resource.query, poster=self)
        self.resource.query_in_column = partial(self.resource.query_in_column, poster=self)
        self.resource.video_detail = partial(self.resource.video_detail, poster=self)

        self.user = User
        self.user.query = partial(self.user.query, poster=self)
        self.user.register = partial(self.user.register, poster=self)
        self.user.update = partial(self.user.update, poster=self)

    @staticmethod
    def auto_init():
        """
        临时生成 init 代码用
        """
        pass
        # model_list = [Banner, Column, Combine, Comment, Message, Order, Praise,
        #               Purchase, PurchaseUser, Resource, User]
        # for m in model_list:
        #     name = m.__name__
        #     name_lower = name.lower()
        #     print('\n        self.{} = {}'.format(name_lower, name))
        #     # setattr(self, name_lower, m)
        #     for k in dir(m):
        #         if '__' in k:
        #             continue
        #         print('        self.{}.{} = partial(self.{}.{}, poster=self)'.format(name_lower, k, name_lower, k))
        #         # setattr(getattr(self, name_lower), k, partial(getattr(getattr(self, name_lower), k), poster=self))
