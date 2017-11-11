import pytest

from hypothesis_drf import from_serializer
from hypothesis import given

from rest_framework import serializers

from django.test import override_settings
from django.conf.urls import url

from . import models


class SubSerializer(serializers.Serializer):
    value = serializers.IntegerField()


class ExampleSerializer(serializers.Serializer):
    """
    Some things are not suitable for direct field test
    """
    read_only = serializers.ReadOnlyField()
    hidden = serializers.HiddenField(default='whatever')

    sub = SubSerializer()
    sub_many = SubSerializer(many=True)
    sub_optional = SubSerializer(required=False)

    method = serializers.SerializerMethodField()

    def get_method(self, obj):
        return "hello"


class ExampleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExampleModel
        fields = '__all__'


class ExampleHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ForeignKeySource
        fields = '__all__'


@given(data=from_serializer(ExampleSerializer))
def test_example_data(data):
    ExampleSerializer(data=data).is_valid(raise_exception=True)


@pytest.mark.django_db
def test_model_serializer():
    @given(data=from_serializer(ExampleModelSerializer))
    def test(data):
        serializer = ExampleModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)

    test()


@override_settings(ROOT_URLCONF=[
    url(r'^example/(?P<pk>.+)/$', lambda: None, name='foreignkeytarget-detail'),
])
@pytest.mark.django_db
def test_hyperlinkedmodel_serializer(rf):
    target = models.ForeignKeyTarget.objects.create(name='some_name')
    models.ForeignKeySource.objects.create(target_id=target.id)

    request = rf.get('/')

    @given(data=from_serializer(ExampleHyperlinkedModelSerializer(context={'request': request})))
    def test(data):
        serializer = ExampleHyperlinkedModelSerializer(data=data)
        serializer.is_valid(raise_exception=True)

    test()
