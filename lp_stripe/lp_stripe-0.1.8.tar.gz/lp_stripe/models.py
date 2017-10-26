from django.contrib.auth import get_user_model
from django.db import models
from .client import Client


User = get_user_model()


class Customer(models.Model):
    user = models.ForeignKey(User, related_name='customer')
    stripe_id = models.CharField(max_length=256)

    def __init__(self, *args, **kwargs):
        self.client = Client()
        super(Customer, self).__init__(*args, **kwargs)


class Subscription(models.Model):
    customer = models.ForeignKey(Customer, related_name='subscription')
    stripe_id = models.CharField(max_length=255)
    verbose_name = models.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.client = Client()
        super(Subscription, self).__init__(*args, **kwargs)

    def cancel(self):
        self.client.cancel_subscription(self.stripe_id)

