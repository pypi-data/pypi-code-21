from rest_framework import serializers
from rest_framework.views import APIView


class SimpleSerializer(serializers.Serializer):
    char = serializers.CharField()


class ErrorView(APIView):

    def get(self, request, *args, **kwargs):
        SimpleSerializer(data={}).is_valid(raise_exception=True)
