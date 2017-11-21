#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import subscription

class BDSubscription(subscription.ESubscription, bd_common.BDCommon):

    @bd_common.handle_error
    def create_s(self):
        api = self._get_api()
        self.approve(type = "new")
        subscription = self.unwrap(default = True)
        subscription = api.create_subscription(subscription)
        subscription = BDSubscription.wrap(subscription)
        return subscription
