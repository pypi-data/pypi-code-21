from django.apps import apps
from rest_framework import serializers


class PolymorphicSerializer(serializers.ModelSerializer):

    def get_child_serializer(self, model):
        assert hasattr(self.Meta, 'child_serializers'), (
            "Class {serializer_class} missing "
            "Meta.child_serializers attribute".format(
                serializer_class=self.__class__.__name__
            )
        )

        child_serializer_class = next((
            s for s in self.Meta.child_serializers
            if model == s.Meta.model), None
        )

        if child_serializer_class is not None:
            return child_serializer_class(self.instance, context=self.context)
        return None

    def get_param_serializer(self):
        content_type = self.context['request']\
            .query_params.get('content_type')

        if content_type is not None:
            try:
                model = apps.get_model(*content_type.split('.'))
            except LookupError:
                return None
            return self.get_child_serializer(model)
        return None

    def get_fields(self):
        fields = super().get_fields()
        instance = self.instance

        if instance is None:
            child_serializer = self.get_param_serializer()
        elif hasattr(instance, '_meta'):
            child_serializer = self.get_child_serializer(instance._meta.model)
        else:
            child_serializer = None

        if child_serializer is not None:
            fields.update(child_serializer.get_fields())

        return fields

    def create(self, validated_data):
        child_serializer = self.get_param_serializer()

        if child_serializer is not None:
            return child_serializer.create(validated_data)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        child_serializer = self.get_child_serializer(instance._meta.model)

        if child_serializer is not None:
            return child_serializer.update(instance, validated_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        child_serializer = self.get_child_serializer(instance._meta.model)

        if child_serializer is not None:
            data.update(child_serializer.to_representation(instance))

        data['content_type'] = '{}.{}'.format(
            instance._meta.app_label,
            instance._meta.model_name)

        return data
