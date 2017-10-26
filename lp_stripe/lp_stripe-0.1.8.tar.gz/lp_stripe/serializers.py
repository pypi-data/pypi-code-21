from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Subscription

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ['customer']


class SubscriptionCreateSerializer(serializers.Serializer):
    source = serializers.CharField()
    plan = serializers.CharField(required=True)

