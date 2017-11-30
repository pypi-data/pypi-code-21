# -*- coding: utf-8 -*-
"""
Conversor de Modelo para Json.

Converte os dados do modelo para o formato JSON
-   Para campos concretos (que possuem dados) é feita a
    conversão pelo código abaixo
-   Para campos relacionais (foreign keys, etc), é selecionada a instancia
    relativa a chave e então lido os campos concretos desta subsintância

PEP8: OK
"""
from base64 import b64encode
from django.utils.encoding import force_bytes

INTEGER_FIELDS = [
    'AutoField',
    'BigIntegerField',
    'IntegerField',
    'PositiveIntegerField',
    'PositiveSmallIntegerField',
    'SmallIntegerField'
]
BINARY_FIELDS = ['BinaryField']
BOOLEAN_FIELDS = ['BooleanField', 'NullBooleanField']
STRING_FIELDS = [
    'CharField',
    'CommaSeparatedIntegerField',
    'EmailField',
    'IPAddressField',
    'GenericIPAddressField',
    'SlugField',
    'TextField',
    'URLField',
    'UUIDField'
]
DATETIME_FIELDS = ['DateField', 'DateTimeField', 'TimeField']
DECIMAL_FIELDS = ['DecimalField']
TIMEDELTA_FIELDS = ['DurationField']
FILE_FIELDS = ['FileField', 'ImageField']
FILEPATH_FIELDS = ['FilePathField']
FLOAT_FIELDS = ['FloatField']


class ModelSerializer(object):

    foreign_fields = ''
    ignore_fields = []

    def __init__(
            self,
            instance=None,
            delete_id=None,
            *args,
            **kwargs):
        super(ModelSerializer, self).__init__(*args, **kwargs)
        self.instance = instance
        self.delete_id = delete_id
        self.dictionary = {}

    def instance_to_dict(self, instance=None):

        if not instance:
            instance = self.instance

        field_list = instance._meta.get_fields(include_hidden=True)
        model_dict = {}

        for field in field_list:
            if field.name in self.ignore_fields:
                continue

            if not field.is_relation:
                field_type = field.get_internal_type()
                field_value = getattr(instance, field.name)
                if field_type in INTEGER_FIELDS or field_type in \
                        STRING_FIELDS or field_type in DECIMAL_FIELDS \
                        or field_type in FLOAT_FIELDS:
                    if field_value is None:
                        model_dict[field.name] = ''
                    elif isinstance(field_value, str):
                        model_dict[field.name] = field_value
                    elif isinstance(field_value, unicode):
                        model_dict[field.name] = \
                            field_value.encode('utf-8')
                    else:
                        model_dict[field.name] = str(field_value)
                elif field_type in BINARY_FIELDS:
                    model_dict[field.name] = b64encode(force_bytes(
                        field_value)).decode('ascii') if field_value else ''
                elif field_type in BOOLEAN_FIELDS:
                    if field_value is not None:
                        model_dict[
                            field.name] = '1' if field_value is True else '0'
                    else:
                        model_dict[field.name] = ''
                elif field_type in DATETIME_FIELDS:
                    if field_value:
                        model_dict[
                            field.name] = {
                            'iso': field_value.strftime(
                                "%Y-%m-%dT%H:%M:%S%z"),
                            'date': field_value.strftime("%Y-%m-%d"),
                            'time': field_value.strftime("%H:%M:%S"),
                            'tz_name': field_value.strftime("%Z"),
                            'tz_value': field_value.strftime("%z"),
                        }
                    else:
                        model_dict[field.name] = ''
                elif field_type in TIMEDELTA_FIELDS:
                    if field_value:
                        model_dict[
                            field.name] = str(field_value.total_seconds())
                    else:
                        model_dict[field.name] = ''
                elif field_type in FILE_FIELDS:
                    if field_value:
                        model_dict[field.name] = {
                            'name': str(field.value.name),
                            'path': str(field_value.path),
                            'url': str(field_value.url)
                        }
                    else:
                        model_dict[field.name] = ''
                elif field_type in FILEPATH_FIELDS:
                    if field_value:
                        model_dict[field.name] = str(field_value.path)
                    else:
                        model_dict[field.name] = ''
                else:
                    raise ValueError(
                        u"Sem conversão para o tipo %s" %
                        (field_type))

        return model_dict

    def related_fields_to_dict(self, response):

        for field in self.foreign_fields:
            if field in self.ignore_fields:
                continue

            if not hasattr(self.instance, field):
                print u"CAMPO %s NÃO EXISTE" % (field)
                continue
            if not self.instance._meta.get_field(field).is_relation:
                print u"CAMPO %s NÃO É DO TIPO RELAÇÃO" % (field)
                continue

            obj = getattr(self.instance, field)
            if hasattr(obj, '_meta'):
                response[field] = self.instance_to_dict(obj)
            elif callable(getattr(obj, 'all', None)):
                response[field] = [
                    self.instance_to_dict(m2m_obj)
                    for m2m_obj in obj.all()
                    if hasattr(m2m_obj, '_meta')
                ]
            else:
                response[field] = ''
        return response

    def serialize(self):

        if not self.model:
            raise ValueError("Modelo não informado")
        elif not self.delete_id:
            if self.instance._meta.model != self.model:
                raise ValueError("Esta classe não manipula o modelo %s" % (
                    self.instance._meta.model_name)
                )

        if self.delete_id:
            self.dictionary = {
                "id": str(self.delete_id),
                "dados_api": {
                    'database_model': self.model._meta.model_name
                }
            }
        else:
            base_response = self.instance_to_dict()
            full_response = self.related_fields_to_dict(base_response)

            self.dictionary = full_response

            self.dictionary['dados_api'] = {
                'database_model': self.instance._meta.model_name
            }

        self.additional_info()

        return self.dictionary

    def additional_info(self):
        pass
