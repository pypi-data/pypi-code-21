import stripe
from .conf import Settings


class Client(object):
    def __init__(self, api_key=None):
        self.settings = Settings()
        self.stripe = stripe
        self.stripe.api_key = api_key if api_key else self.settings.api_key

    def create_customer(self, description=None, source=None):
        if not description or not source:
            raise Exception('description and source fields are required')

        return self.stripe.Customer.create(description=description, source=source)

    def create_subscription(self, customer=None, plan=None):
        if not customer or not plan:
            raise Exception('customer and plan fields are required')

        return self.stripe.Subscription.create(customer=customer, items=[{'plan': plan}])

    def cancel_subscription(self, subscription=None):
        if not subscription:
            raise Exception('subscription field is required')

        sub = self.stripe.Subscription.retrieve(subscription)
        sub.delete()

    def plans(self):
        return self.stripe.Plan.list()
