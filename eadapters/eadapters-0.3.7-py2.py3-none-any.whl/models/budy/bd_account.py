#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import bd_bag
from . import bd_order
from . import bd_common
from . import bd_address

from .. import account

class BDAccount(account.EAccount, bd_common.BDCommon):

    @classmethod
    def wrap(cls, models, build = True, handler = None, **kwargs):
        def handler(model):
            bag_key = model.get("bag_key", None)
            if bag_key: model.update(
                bag = bd_bag.BDBag.wrap(
                    dict(
                        key = cls.bd_unicode_d(model, "bag_key")
                    )
                )
            )

        return super(BDAccount, cls).wrap(
            models,
            build = build,
            handler = handler,
            **kwargs
        )

    @classmethod
    @bd_common.handle_error
    def login(cls, username, password):
        api = cls._get_api_g(username = username)
        api.password = password

        try:
            api.login()
            api.key_bag()
            account = api.me_account()
        except appier.HTTPError as error:
            bd_common._handle_error(error, code = 403)

        account = cls.wrap(account)
        return account

    @classmethod
    @bd_common.handle_error
    def confirm_s(cls, token):
        api = cls._get_api_g()
        account = api.confirm_account(token)
        account = cls.wrap(account)
        return account

    @classmethod
    @bd_common.handle_error
    def me(cls):
        api = cls._get_api_g()
        account = api.me_account()
        return cls.wrap(account)

    @bd_common.handle_error
    def create_s(self, pre_enabled = False):
        api = self._get_api()
        self.approve(type = "new")
        account = self.unwrap(default = True)
        account = api.create_account(account, pre_enabled = pre_enabled)
        account = BDAccount.wrap(account)
        return account

    @bd_common.handle_error
    def recover_s(self):
        api = self._get_api()
        api.recover_account(self.username)

    @bd_common.handle_error
    def reset_s(self, password, token):
        api = self._get_api()
        api.reset_account(self.username, password, token)

    @classmethod
    @bd_common.handle_error
    def avatar_me(cls):
        api = cls._get_api_g()
        avatar = api.avatar_me_account()
        return avatar

    @classmethod
    @bd_common.handle_error
    def addresses_me(cls):
        api = cls._get_api_g()
        addresses = api.addresses_me_account()
        addresses = bd_address.BDAddress.wrap(addresses)
        return addresses

    @bd_common.handle_error
    def update_me_s(self):
        api = self._get_api()
        self.approve()
        account = self.unwrap(default = True)
        avatar = account.pop("avatar")
        password = account.pop("password")
        if avatar: account["avatar"] = avatar
        if password: account["password"] = password
        api.update_me_account(account)
        account = api.me_account()
        return BDAccount.wrap(account)

    @bd_common.handle_error
    def get_address(self, address_id):
        api = self._get_api()
        address = api.get_address(address_id)
        address = bd_address.BDAddress.wrap(address)
        return address

    @bd_common.handle_error
    def create_address_s(self, address):
        api = self._get_api()
        address.approve(type = "new")
        address = address.unwrap(default = True)
        address = api.create_addresses_me_account(address)
        address = bd_address.BDAddress.wrap(address)
        return address

    @bd_common.handle_error
    def update_address_s(self, address):
        api = self._get_api()
        address.approve()
        address_key = address.key
        address = address.unwrap(default = True)
        api.update_address(address_key, address)
        return self.get_address(address_key)

    @bd_common.handle_error
    def delete_address_s(self, address_id):
        api = self._get_api()
        api.delete_address_me_account(address_id)

    @bd_common.handle_error
    def orders(self):
        api = self._get_api()
        orders = api.orders_me_account()
        return bd_order.BDOrder.wrap(orders)
