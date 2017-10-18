from .api import BaseModelManager


class PaymentMethodManager(BaseModelManager):
    namespace = ['billing', 'methods']


class PaymentChargeManager(BaseModelManager):
    namespace = ['billing', 'charges']


class SubscriptionPlanManager(BaseModelManager):
    namespace = ['billing', 'subscriptions']
