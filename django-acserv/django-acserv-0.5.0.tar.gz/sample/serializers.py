import timeago
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from sample.models import ClientSession

User = get_user_model()


class ClientSessionSerializer(serializers.ModelSerializer):
    created_time_ago = serializers.SerializerMethodField()

    class Meta:
        model = ClientSession
        fields = ('app', 'os', 'ip', 'created_time_ago', 'device_id')

    def get_os(self, cs: ClientSession):
        return self.get_os_brand(cs.os)

    def get_created_time_ago(self, cs: ClientSession):
        return timeago.format(cs.created_at, timezone.now(), 'zh_CN')
