import os
import json

CLASS_NAME = u'class_name'
KEY = u'key'
MANDATORY = u'mandatory'
OPTIONAL = u'optional'
PROPERTY = u'property'
TYPE = u'type'
PROPERTY_NAME = u'property_name'
PROPERTIES = u'properties'
DEFAULT = u'default'
ATTRIBUTES = u'attributes'
FILENAME = u"filename"
MIXIN_IMPORTS = u'mixin_imports'


class MandatoryFieldMissing(Exception):
    pass


class JsonApiPropertiesClass(object):

    def __init__(self,
                 response,
                 parent=None):
        """
        Provides base class for API classes that use properties instead of
        keys into a dictionary.

        It's not mandatory to call __init__. You can explicitly set self.response_dict instead
        if that makes more sense in your subclass
        s
        :param response: A dictionary or JSON string that can be converted to a dictionary.
                         (Don't supply lists)
        :param parent: Can pass a parent object, so that a subclass can access its properties
        """
        # TODO: Add requests response object handling
        try:
            self.response_dict = json.loads(response)
        except:
            self.response_dict = response

        self.parent = parent
        super(JsonApiPropertiesClass, self).__init__()  # Required for co-operative multiple inheritance

    def mandatory(self,
                  key):
        try:
            return self.response_dict[key]
        except KeyError:
            raise MandatoryFieldMissing(key)

    def optional(self,
                 key,
                 default=None):
        return self.response_dict.get(key, default)

    def get_property(self,
                     item):
        try:
            return getattr(self, item)
        except AttributeError:
            pass
        try:
            return getattr(self.parent.item)
        except AttributeError as ae:
            pass
        try:
            return self.parent.get_property(item)
        except AttributeError as ae:
            raise ValueError(u'Could not find "{item}" in object tree'.format(item=item))

