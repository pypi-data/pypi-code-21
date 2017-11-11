from .test_fields import fields, related_fields
from .test_serializers import ExampleSerializer
from rest_framework import serializers, fields as drf_fields


def test_missing_coverage():

    covered_related = set()
    for field_type, kwargs in related_fields:
        kwargs = kwargs.copy()
        kwargs.setdefault('queryset', True)
        covered_related.add(type(field_type(**kwargs.copy())))

    covered = (
        covered_related |
        {type(field) for field in fields} |
        {type(field) for field in ExampleSerializer().fields.values()} |
        {
            serializers.URLField,
            serializers.HyperlinkedModelSerializer,
            serializers.ModelSerializer,
        })

    def all_subclasses(cls):
        yield cls

        for sub_cls in cls.__subclasses__():
            yield from all_subclasses(sub_cls)

    missing = set(all_subclasses(serializers.Field)) - covered

    missing = {
        cls
        for cls in missing
        if not any((
            # Some meta-magic going on with serializers.Serializer causes false positive
            cls.__module__ == 'rest_framework.serializers' and cls.__name__ == 'Serializer',

            # N/A declared here
            cls.__module__ .startswith('tests.')
        ))
    }

    known_missing = {
            # TODO
            serializers.FileField,
            serializers.FilePathField,
            serializers.ImageField,
            serializers.ModelField,

            # N/A
            serializers.BaseSerializer,
            serializers.RelatedField,
            serializers.Field,
            drf_fields._UnvalidatedField,  # TODO, what is it?
        }
    assert missing == known_missing
