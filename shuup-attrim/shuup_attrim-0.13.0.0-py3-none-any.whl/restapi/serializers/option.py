from rest_framework import serializers

from attrim.models import Class, Option, Attribute
from attrim.restapi.serializers.fields import OptionValueField


class OptionSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    cls = serializers.PrimaryKeyRelatedField(queryset=Class.objects)
    attributes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Attribute.objects,
        required=False,
    )
    value = OptionValueField()
    order = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Option
        fields = ('pk', 'cls', 'attributes', 'value', 'order')

    def create(self, validated_data: dict) -> Option:
        return Option.objects.create(**validated_data)

    def update(self, instance: Option, validated_data: dict) -> Option:
        instance.cls = validated_data.get('cls', instance.cls)
        instance.set_value(validated_data.get('value', instance.get_value))
        if 'attributes' in validated_data:
            instance.attributes.set(validated_data['attributes'])
        instance.order = validated_data.get('order', None)
        instance.save()
        return instance
