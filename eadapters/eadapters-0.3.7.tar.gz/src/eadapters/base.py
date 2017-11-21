#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid

import appier

class BaseAdapter(object):

    def __init__(self, *args, **kwargs):
        self.api = None
        self.api_m = dict()
        self.uuid = kwargs.get("uuid", str(uuid.uuid4()))

    def get_context(self):
        return dict(uuid = self.uuid)

    def set_context(self, context):
        for name, value in appier.legacy.iteritems(context):
            setattr(self, name, value)

    def is_auth(self):
        raise appier.NotImplementedError()

    def get_country(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_country(self, country, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_currency(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_currency(self, currency, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_language(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_language(self, language, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_country_c(self, country_code, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_countries(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_states(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_cities(self, country_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_products(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_product(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def search_products(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def related_product(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def share_product(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_brands(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_brand(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_categories(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_category(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def slug_category(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_collections(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_collection(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def slug_collection(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_colors(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_color(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def slug_color(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def sort_colors(self, colors):
        colors.sort(key = lambda item: item.name)

    def create_subscription(self, subscription, *args, **kwargs):
        raise appier.NotImplementedError()

    def login_account(self, username, password, *args, **kwargs):
        raise appier.NotImplementedError()

    def me_account(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def create_account(self, account, *args, **kwargs):
        raise appier.NotImplementedError()

    def update_account(self, account, *args, **kwargs):
        raise appier.NotImplementedError()

    def confirm_account(self, token, *args, **kwargs):
        raise appier.NotImplementedError()

    def recover_password_account(self, username, *args, **kwargs):
        raise appier.NotImplementedError()

    def reset_password_account(self, username, password, token, *args, **kwargs):
        raise appier.NotImplementedError()

    def avatar_me_account(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def create_address(self, address, *args, **kwargs):
        raise appier.NotImplementedError()

    def mandatory_attributes_address(self, country_code, *args, **kwargs):
        raise appier.NotImplementedError()

    def addresses_account(self, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def address_account(self, address_id, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def create_address_account(self, address, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def update_address_account(self, address, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def delete_address_account(self, address_id, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def orders_account(self, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def empty_bag(self, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def create_order_bag(self, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_order_checkout(self, id, *args, **kwargs):
        return self.get_order(id, *args, **kwargs)

    def get_order(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_meta_order(self, id, name, value, *args, **kwargs):
        raise appier.NotImplementedError()

    def wait_payment_order(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def pay_order(self, id, payment_data, *args, **kwargs):
        raise appier.NotImplementedError()

    def end_pay_order(self, id, payment_data, *args, **kwargs):
        raise appier.NotImplementedError()

    def cancel_order(self, id, cancel_data, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_shipping_address_order(self, address_id, order_id, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_billing_address_order(self, address_id, order_id, account_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_store_shipping_order(self, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_store_billing_order(self, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_ip_address_order(self, ip_address, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_email_order(self, email, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_gift_wrap_order(self, gift_wrap, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_referral_order(self, voucher_id, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def set_voucher_order(self, voucher_id, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def returns_order(self, order_id, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_return(self, id, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_payment_methods(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def list_card_payment_methods(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def confirm_payment(self, transation_id, parameters, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_bag(self, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def add_bag_line(self, product_id, quantity = 1, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def update_bag_line(self, bag_line, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def remove_bag_line(self, line_id, bag_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def get_wishlist(self, wishlist_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def add_wishlist_line(
        self,
        product_id,
        quantity = 1,
        size = None,
        scale = None,
        wishlist_id = None,
        *args,
        **kwargs
    ):
        raise appier.NotImplementedError()

    def update_wishlist_line(self, line, wishlist_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def remove_wishlist_line(self, line_id, wishlist_id = None, *args, **kwargs):
        raise appier.NotImplementedError()

    def _get_api(self, *args, **kwargs):
        raise appier.NotImplementedError()

    def _convert(self, kwargs, old, new, delete = True):
        if not old in kwargs: return
        value = kwargs[old]
        kwargs[new] = value
        if delete: del kwargs[old]
