import pytest

from hypothesis_drf import from_serializer, from_field
from hypothesis import settings as hypothesis_settings, given, strategies as st

from django.test import override_settings
from django.conf.urls import url

from rest_framework import serializers

from . import models


class CustomField(serializers.CharField):
    hypothesis_strategy = st.sampled_from(('foo', 'bar'))

    def run_validators(self, value):
        super().run_validators(value)
        assert value in ('foo', 'bar')


fields = (
    serializers.CharField(),
    serializers.CharField(max_length=10),
    serializers.CharField(min_length=50),
    serializers.CharField(allow_blank=True),
    serializers.CharField(required=True),

    serializers.IntegerField(),
    serializers.IntegerField(required=False),
    serializers.IntegerField(min_value=100),
    serializers.IntegerField(max_value=-10),
    serializers.IntegerField(min_value=3, max_value=100),

    serializers.FloatField(),
    serializers.FloatField(min_value=1024.31),
    serializers.FloatField(max_value=1.30),
    serializers.FloatField(min_value=-1.31, max_value=0.13),

    serializers.BooleanField(),
    serializers.BooleanField(required=False, default=True),
    serializers.BooleanField(required=False),
    serializers.NullBooleanField(),

    serializers.EmailField(),

    serializers.ChoiceField(choices={'a', 'b', 'c'}),
    serializers.MultipleChoiceField(choices={'a', 'b', 'c'}),

    serializers.DateField(),
    serializers.DateTimeField(),
    serializers.TimeField(),

    serializers.DecimalField(max_digits=2, decimal_places=1),
    serializers.DecimalField(max_digits=1, decimal_places=0),
    serializers.DecimalField(max_digits=3, decimal_places=2, min_value=3, max_value=5),
    serializers.DecimalField(max_digits=4, decimal_places=1, max_value=0),

    serializers.DurationField(),

    serializers.UUIDField(),

    serializers.ListField(child=serializers.IntegerField()),
    serializers.ListField(child=serializers.IntegerField(), allow_empty=False),
    serializers.ListField(child=serializers.IntegerField(), max_length=10),
    serializers.ListField(child=serializers.IntegerField(), min_length=3),

    serializers.RegexField(r'^[abc]+$'),

    serializers.IPAddressField(),
    serializers.IPAddressField(protocol='ipv4'),
    serializers.IPAddressField(protocol='ipv6'),

    serializers.DictField(child=serializers.IntegerField()),

    serializers.JSONField(allow_null=True),
    serializers.JSONField(binary=True, allow_null=True),
    serializers.JSONField(allow_null=False),
    serializers.JSONField(binary=True, allow_null=False),

    serializers.SlugField(),
    serializers.SlugField(allow_unicode=True),

    # Tested separetely as it is slow
    # serializers.URLField(),

    CustomField()

    # TODO
    # FileField, FilePathField,
    # ImageField,
    # ModelField,
)


@pytest.mark.parametrize(
    'field,strategy',
    [
        pytest.param(field, from_field(field), id=str(field))
        for field in fields
    ]
)
def test_field_strategy(field, strategy):
    @given(value=strategy)
    def test_field(value):
        try:
            field.run_validation(value)
        except serializers.SkipField:
            # When field is not required and got an `empty` value
            pass

    test_field()


# This can be absurdly slow on first run
@hypothesis_settings(deadline=60000)
@given(from_field(serializers.URLField()))
def test_url_field(url):
    serializers.URLField().run_validation(url)


related_fields = (
    (serializers.PrimaryKeyRelatedField, {}),
    (serializers.PrimaryKeyRelatedField, {'many': True}),

    (serializers.SlugRelatedField, {'slug_field': 'name'}),
    (serializers.StringRelatedField, {'queryset': None}),
    (serializers.HyperlinkedIdentityField,
        {'queryset': None, 'view_name': 'example', 'lookup_field': 'name', 'lookup_url_kwarg': 'name'}),

    (serializers.HyperlinkedRelatedField,
        {'view_name': 'example', 'lookup_field': 'name', 'lookup_url_kwarg': 'name'}),
)


@override_settings(ROOT_URLCONF=[
    url(r'^example/(?P<name>.+)/$', lambda: None, name='example'),
])
@pytest.mark.parametrize(
    'field_type,kwargs',
    [
        pytest.param(field_type, kwargs, id=f'{field_type.__name__}(**{kwargs})')
        for field_type, kwargs in related_fields
    ]
)
@pytest.mark.django_db
def test_related_field(field_type, kwargs, rf):
    target = models.ForeignKeyTarget.objects.create(name='some_name')
    models.ForeignKeySource.objects.create(target_id=target.id)

    if 'queryset' not in kwargs:
        kwargs['queryset'] = models.ForeignKeyTarget.objects.all()

    class RelatedFieldSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.ForeignKeySource
            fields = ('target', )

        target = field_type(**kwargs)

    request = rf.get('/')

    @given(data=from_serializer(RelatedFieldSerializer(context={'request': request})))
    def test(data):
        RelatedFieldSerializer(data=data, context={'request': True}).is_valid(raise_exception=True)

    test()
