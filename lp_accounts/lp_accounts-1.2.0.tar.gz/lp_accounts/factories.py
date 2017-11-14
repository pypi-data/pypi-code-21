from collections import OrderedDict
from rest_framework import serializers


def serializer_factory(mdl):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = mdl
            fields = '__all__'

    return Serializer
