# -*- coding: utf-8 -*-

# zope imports
from zope import schema

# local imports
from ps.zope.i18nfield import (
    interfaces,
    storage,
    utils,
)

_marker = dict()


class I18NFieldProperty(schema.fieldproperty.FieldProperty):
    """Base class for I18N properties."""

    def __init__(self, field, name=None, value_converters=None):
        if not interfaces.II18NField.providedBy(field):
            raise ValueError(
                u'Provided field must implement II18NField interface.'
            )
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name
        if value_converters is None:
            self.__value_converters = ()
        else:
            self.__value_converters = value_converters

    def __get__(self, instance, klass):
        if instance is None:
            return self
        value = instance.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(instance)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        return value

    def __set__(self, instance, value):
        # prepare the values
        value = self.prepare_dict(value)
        old_value = getattr(instance, self.__name, None)
        if old_value is None and isinstance(value, basestring):
            value = storage.I18NDict.from_text(value)
        if isinstance(value, storage.I18NDict):
            validate_dict = value.to_dict()
            storage_dict = value
            storage_dict.clear()
        else:
            validate_dict = value
            storage_dict = storage.I18NDict()

        assert isinstance(validate_dict, dict), 'validate_dict must be dict'
        assert isinstance(storage_dict, storage.I18NDict), \
            'storage_dict must be I18NDict'

        # field validation
        field = self.__field.bind(instance)
        field.validate(validate_dict)
        if field.readonly and self.__name in instance.__dict__:
            raise ValueError(self.__name, u'Field is readonly')

        # set the new I18nDict
        storage_dict.default_language = field._default_language
        storage_dict.required = field.required
        storage_dict.update(validate_dict)
        instance.__dict__[self.__name] = storage_dict

    def __getattr__(self, name):
        return getattr(self.__field, name)

    def prepare_dict(self, value):
        """Prepare the values of the dict by removing any empty values and
        passing the remaining values through any converters associated with
        this field.

        :param value: Value that will be set with the FieldProperty
        :type value: dict
        :returns: The prepared values
        :rtype: dict
        """
        if value is None:
            return {}
        if isinstance(value, dict) or isinstance(value, storage.I18NDict):
            for lang in value.keys():
                if not value[lang]:
                    del value[lang]
            for converter in self.__value_converters:
                for lang in value:
                    value[lang] = converter(value[lang])
        return value


class I18NTextProperty(I18NFieldProperty):
    """I18n property to handle Text and TextLine values"""

    def __init__(self, field, name=None):
        super(I18NTextProperty, self).__init__(
            field,
            name,
            value_converters=(utils.to_unicode,)
        )
