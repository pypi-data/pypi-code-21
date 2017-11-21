#!/usr/bin/python
# -*- coding: utf-8 -*-

import budy
import appier

from . import base
from . import models

class BudyAdapter(base.BaseAdapter):

    def __init__(
        self,
        username = None,
        password = None,
        session_id = None,
        bag_key = None,
        country = None,
        currency = None,
        language = None,
        context_callback = None,
        *args,
        **kwargs
    ):
        base.BaseAdapter.__init__(self, *args, **kwargs)
        self.username = appier.conf("ADAPTER_USERNAME", None)
        self.password = appier.conf("ADAPTER_PASSWORD", None)
        self.session_id = appier.conf("ADAPTER_SESSION_ID", None)
        self.bag_key = appier.conf("ADAPTER_BAG_KEY", None)
        self.country = appier.conf("ADAPTER_COUNTRY", "US")
        self.currency = appier.conf("ADAPTER_CURRENCY", "USD")
        self.language = appier.conf("ADAPTER_LANGUAGE", "en-US")
        self.username = username or self.username
        self.password = password or self.password
        self.session_id = session_id or self.session_id
        self.bag_key = bag_key or self.bag_key
        self.country = country or self.country
        self.currency = currency or self.currency
        self.language = language or self.language
        self.context_callback = context_callback

    def get_context(self):
        context = base.BaseAdapter.get_context(self)
        context.update(
            username = self.username,
            password = self.password,
            session_id = self.session_id,
            bag_key = self.bag_key,
            country = self.country,
            currency = self.currency,
            language = self.language
        )
        return context

    def is_auth(self):
        api = self._get_api()
        return api.is_auth()

    def get_country(self, *args, **kwargs):
        return self.country

    def set_country(self, country, *args, **kwargs):
        self.country = country
        self._flush_context()

    def get_currency(self, *args, **kwargs):
        return self.currency

    def set_currency(self, currency, *args, **kwargs):
        self.currency = currency
        self._flush_context()

    def get_language(self, *args, **kwargs):
        return self.language

    def set_language(self, language, *args, **kwargs):
        base, country = language.split("_")
        language = "%s-%s" % (base, country.upper())
        self.language = language
        self._flush_context()

    def get_country_c(self, country_code, *args, **kwargs):
        country = models.BDCountry.get_c(country_code)
        if not country: return dict(
            iso = country_code,
            currency = kwargs.get("currency", "USD"),
            locale = kwargs.get("locale", "en_us")
        )
        currency = country.get_currency()
        locale = country.locale
        locale = locale.lower().replace("-", "_")
        return dict(
            iso = country.country_code,
            currency = currency.currency_code,
            locale = locale
        )

    def list_countries(self, *args, **kwargs):
        return models.BDCountry.list(*args, **kwargs)

    def list_products(self, *args, **kwargs):
        api = self._get_api()
        self._normalize(kwargs)
        products = api.list_products(*args, **kwargs)
        products = models.BDProduct.wrap(products)
        return products

    def get_product(self, id, *args, **kwargs):
        api = self._get_api()
        product = api.get_product(id)
        product = models.BDProduct.wrap(product)
        return product

    def search_products(self, *args, **kwargs):
        api = self._get_api()
        self._normalize(kwargs)
        products = api.search_products(*args, **kwargs)
        products = models.BDProduct.wrap(products)
        return products

    def related_product(self, id, *args, **kwargs):
        api = self._get_api()
        product = api.get_product(id)
        product = models.BDProduct.wrap(product)
        related = product.related(*args, **kwargs)
        return related

    def share_product(self, id, *args, **kwargs):
        api = self._get_api()
        product = api.get_product(id)
        product = models.BDProduct.wrap(product)
        share = product.share(*args, **kwargs)
        return share

    def list_categories(self, *args, **kwargs):
        api = self._get_api()
        categories = api.list_categories(*args, **kwargs)
        categories = models.BDCategory.wrap(categories)
        return categories

    def get_category(self, id, *args, **kwargs):
        api = self._get_api()
        category = api.get_category(id)
        category = models.BDCategory.wrap(category)
        return category

    def slug_category(self, slug, *args, **kwargs):
        api = self._get_api()
        category = api.slug_category(slug)
        category = models.BDCategory.wrap(category)
        return category

    def list_collections(self, *args, **kwargs):
        api = self._get_api()
        collections = api.list_collections(*args, **kwargs)
        collections = models.BDCollection.wrap(collections)
        return collections

    def get_collection(self, id, *args, **kwargs):
        api = self._get_api()
        collection = api.get_collection(id)
        collection = models.BDCollection.wrap(collection)
        return collection

    def slug_collection(self, slug, *args, **kwargs):
        api = self._get_api()
        collection = api.slug_collection(slug)
        collection = models.BDCollection.wrap(collection)
        return collection

    def list_colors(self, *args, **kwargs):
        api = self._get_api()
        colors = api.list_colors(*args, **kwargs)
        colors = models.BDColor.wrap(colors)
        return colors

    def get_color(self, id, *args, **kwargs):
        api = self._get_api()
        color = api.get_color(id)
        color = models.BDColor.wrap(color)
        return color

    def slug_color(self, slug, *args, **kwargs):
        api = self._get_api()
        color = api.slug_color(slug)
        color = models.BDColor.wrap(color)
        return color

    def create_subscription(self, subscription, *args, **kwargs):
        subscription = models.BDSubscription(subscription.model)
        return subscription.create_s()

    def login_account(self, username, password, *args, **kwargs):
        account = models.BDAccount.login(
            username = username,
            password = password
        )
        old_key = self.bag_key
        self.username = username
        self.password = password
        self._key_bag()
        if old_key: account.bag.merge_s(old_key)
        return account

    def me_account(self, *args, **kwargs):
        account = models.BDAccount.me()
        return account

    def create_account(self, account, *args, **kwargs):
        pre_enabled = kwargs.get("pre_enabled", False)
        account = models.BDAccount(account.model)
        return account.create_s(pre_enabled = pre_enabled)

    def update_account(self, account, *args, **kwargs):
        account = models.BDAccount(account.model)
        account = account.update_me_s()
        self._flush_context()
        return account

    def confirm_account(self, token, *args, **kwargs):
        models.BDAccount.confirm_s(token)

    def recover_password_account(self, username, *args, **kwargs):
        account = models.BDAccount.get_l(username = username)
        account.recover_s()

    def reset_password_account(self, username, password, token, *args, **kwargs):
        account = models.BDAccount.get_l(username = username)
        account.reset_s(password, token)

    def avatar_me_account(self, *args, **kwargs):
        avatar = models.BDAccount.avatar_me()
        return avatar

    def mandatory_attributes_address(self, country_code, *args, **kwargs):
        return [
            "country",
            "city",
            "first_name",
            "last_name",
            "postal_code",
            "phone_number",
            "address"
        ]

    def create_address(self, address, *args, **kwargs):
        address = models.BDAddress(address.model)
        return address.create_s()

    def addresses_account(self, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        addresses = models.BDAccount.addresses_me()
        return addresses

    def address_account(self, address_id, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        account = models.BDAccount.me()
        return account.get_address(address_id)

    def create_address_account(self, address, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        account = models.BDAccount.me()
        address = models.BDAddress(address.model)
        return account.create_address_s(address)

    def update_address_account(self, address, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        account = models.BDAccount.me()
        address = models.BDAddress(address.model)
        return account.update_address_s(address)

    def delete_address_account(self, address_id, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        account = models.BDAccount.me()
        account.delete_address_s(address_id)

    def orders_account(self, account_id = None, *args, **kwargs):
        if not account_id == None: raise appier.NotImplementedError()
        account = models.BDAccount.me()
        return account.orders()

    def empty_bag(self, bag_id = None, *args, **kwargs):
        bag_id = bag_id or self.bag_key
        bag = models.BDBag.get_l(key = bag_id)
        return bag.empty_s()

    def create_order_bag(self, bag_id = None, *args, **kwargs):
        bag_id = bag_id or self.bag_key
        bag = models.BDBag.get_l(key = bag_id)
        return bag.create_order_s()

    def get_order(self, id, *args, **kwargs):
        return models.BDOrder._get(id)

    def set_meta_order(self, id, name, value, *args, **kwargs):
        order = models.BDOrder.get_l(key = id)
        order.set_meta_s(name, value)

    def wait_payment_order(self, id, *args, **kwargs):
        order = models.BDOrder.get_l(key = id)
        return order.wait_payment_s()

    def pay_order(self, id, payment_data, *args, **kwargs):
        order = models.BDOrder.get_l(key = id)
        return order.pay_s(payment_data)

    def end_pay_order(self, id, payment_data, *args, **kwargs):
        order = models.BDOrder.get_l(key = id)
        return order.end_pay_s(payment_data)

    def cancel_order(self, id, cancel_data, *args, **kwargs):
        order = models.BDOrder.get_l(key = id)
        return order.cancel_s(cancel_data)

    def set_shipping_address_order(self, address_id, order_id, account_id = None, *args, **kwargs):
        account = models.BDAccount.me()
        address = account.get_address(address_id)
        order = models.BDOrder.get_l(key = order_id)
        address = address.unwrap(default = True)
        order.set_shipping_address_s(address)

    def set_billing_address_order(self, address_id, order_id, account_id = None, *args, **kwargs):
        account = models.BDAccount.me()
        address = account.get_address(address_id)
        order = models.BDOrder.get_l(key = order_id)
        address = address.unwrap(default = True)
        order.set_billing_address_s(address)

    def set_store_shipping_order(self, order_id, *args, **kwargs):
        order = models.BDOrder.get_l(key = order_id)
        order.set_store_shipping_s()

    def set_store_billing_order(self, order_id, *args, **kwargs):
        order = models.BDOrder.get_l(key = order_id)
        order.set_store_billing_s()

    def set_ip_address_order(self, ip_address, order_id, *args, **kwargs):
        order = models.BDOrder.get_l(key = order_id)
        order.set_ip_address_s(ip_address)

    def set_email_order(self, email, order_id, *args, **kwargs):
        order = models.BDOrder.get_l(key = order_id)
        order.set_email_s(email)

    def set_gift_wrap_order(self, gift_wrap, order_id, *args, **kwargs):
        order = models.BDOrder.get_l(key = order_id)
        order.set_gift_wrap_s(gift_wrap)

    def set_referral_order(self, referral_id, order_id, *args, **kwargs):
        referral = models.BDReferral.get_l(name = referral_id)
        order = models.BDOrder.get_l(key = order_id)
        order.set_referral_s(referral)

    def set_voucher_order(self, voucher_id, order_id, *args, **kwargs):
        voucher = models.BDVoucher.get_l(key = voucher_id)
        order = models.BDOrder.get_l(key = order_id)
        order.set_voucher_s(voucher)

    def list_card_payment_methods(self, *args, **kwargs):
        return [
            models.BDCardPaymentMethod(
                id_str = "visa",
                name = "Visa",
                type = "credit_card"
            ),
            models.BDCardPaymentMethod(
                id_str = "mastercard",
                name = "MasterCard",
                type = "credit_card"
            ),
            models.BDCardPaymentMethod(
                id_str = "american_express",
                name = "American Express",
                type = "credit_card"
            )
        ]

    def get_bag(self, bag_id = None, *args, **kwargs):
        self._ensure_bag()
        bag_id = bag_id or self.bag_key
        return models.BDBag._get(bag_id)

    def add_bag_line(self, product_id, quantity = 1, bag_id = None, *args, **kwargs):
        size = kwargs.get("size", None)
        scale = kwargs.get("scale", None)
        meta = kwargs.get("meta", None)
        convert = kwargs.get("convert", True)
        self._ensure_bag()
        if convert: product_id = self._product_id_to_id(product_id)
        bag_id = bag_id or self.bag_key
        bag = models.BDBag._get(bag_id)
        bag.add_line_s(
            product_id,
            quantity,
            size = size,
            scale = scale,
            meta = meta,
        )

    def remove_bag_line(self, bag_line_id, bag_id = None, *args, **kwargs):
        self._ensure_bag()
        bag_id = bag_id or self.bag_key
        bag = models.BDBag.get_l(key = bag_id)
        bag.remove_line_s(bag_line_id)

    def _product_id_to_id(self, product_id):
        api = self._get_api()
        kwargs = {
            "filters[]" : "product_id:equals:%s" % product_id
        }
        products = api.list_products(**kwargs)
        if not products: return product_id
        first_product = products[0]
        return first_product["id"]

    def _on_auth(self, contents):
        self.session_id = contents.get("session_id", None)
        self._flush_context()

    def _key_bag(self):
        api = self._get_api()
        contents = api.key_bag()
        self.bag_key = contents["key"]
        self._flush_context()
        return self.bag_key

    def _ensure_bag(self):
        if self.bag_key: return
        self._key_bag()

    def _flush_context(self):
        if not self.context_callback: return
        context = self.get_context()
        self.context_callback(context)

    def _get_api(self, *args, **kwargs):
        username = kwargs.get("username", self.username)
        password = kwargs.get("password", self.password)
        session_id = kwargs.get("session_id", self.session_id)
        country = kwargs.get("country", self.country)
        currency = kwargs.get("currency", self.currency)
        language = kwargs.get("language", self.language)
        if self.api: return self._apply_api(*args, **kwargs)

        api = budy.API(
            username = username,
            password = password,
            session_id = session_id,
            country = country,
            currency = currency,
            language = language
        )
        self.api = api
        api.bind("auth", self._on_auth)
        return api

    def _apply_api(self, *args, **kwargs):
        for key, value in appier.legacy.iteritems(kwargs):
            if not value: continue
            setattr(self.api, key, value)
        return self.api

    def _normalize(self, kwargs):
        self._sort(kwargs)
        self._convert(kwargs, "filter", "find_s")

    def _sort(self, kwargs, delete = True):
        if not "sort" in kwargs: return
        if not kwargs["sort"]: return
        kwargs["sort"] = "%s:%s" % kwargs["sort"][0]
