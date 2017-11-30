from parler.utils.context import switch_language
from rest_framework import serializers
from shuup.api.fields import EnumField
from shuup.core.models import ProductType
from django.utils.translation import ugettext as _
from shuup_utils.lang_constants import DEFAULT_LANG

from attrim.models import Class, Option, Attribute
from attrim.models.type import Type
from attrim.restapi.serializers.fields import TransStrField
from attrim.trans_str import TransStr


class ClassSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    code = serializers.CharField()
    type = EnumField(enum=Type)
    name = TransStrField(required=True)
    product_type = serializers.PrimaryKeyRelatedField(queryset=ProductType.objects)
    attributes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Attribute.objects,
        required=False,
    )
    options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Option.objects,
        required=False,
    )

    class Meta:
        model = Option
        fields = ('pk', 'code', 'type', 'name', 'product_type', 'attributes', 'options')

    def create(self, validated_data: dict) -> Class:
        name = validated_data.pop('name') # type: TransStr
        cls = Class.objects.create(**validated_data)
        for lang_code, value in name:
            with switch_language(cls, lang_code):
                cls.name = value
        cls.save()
        return cls

    def update(self, instance: Class, validated_data: dict) -> Class:
        instance.code = validated_data.get('code', instance.code)
        instance.type = validated_data.get('type', instance.type)
        instance.product_type = validated_data.get('product_type', instance.product_type)
        if 'name' in validated_data:
            instance.set_name(validated_data['name'])
        if 'attributes' in validated_data:
            instance.attributes.set(validated_data['attributes'])
        if 'options' in validated_data:
            instance.options.set(validated_data['options'])
        instance.save()
        return instance

    def validate_name(self, name_trans_str: TransStr) -> TransStr:
        if name_trans_str.is_empty():
            raise serializers.ValidationError(
                _('The name field is required')
            )
        name_trans_def = name_trans_str.get_value(lang_code=DEFAULT_LANG)
        if name_trans_def == '' or name_trans_def is None:
            raise serializers.ValidationError(
                _('An empty value for the default translation of the name is not allowed')
            )
        return name_trans_str
