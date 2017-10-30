from rest_framework import serializers
from .models import NotificationReceipt


class NotificationReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationReceipt
        fields = '__all__'
