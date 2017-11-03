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


class JsonApiPropertiesClassCreator(object):

    MANDATORY = MANDATORY
    OPTIONAL = OPTIONAL
    PROPERTY = PROPERTY
    PROPERTIES = PROPERTIES
    DEFAULT = DEFAULT
    TYPE = TYPE

    def __init__(self,
                 class_name,
                 attributes=None,
                 property_name=None,
                 mixin_imports=None,
                 key=None,
                 parent_mixin_imports=None,):
        """
        Create a JsonApiPropertiesClass subclass so that attributes of
        the dictionary can be accessed with dot notation and with
        more meaningful names.

        Can also generate mixins for creating the DictionaryResponses
        inside other objects as properties

        The code produced can be written to a file for importing
        or can be used to call exec() dynamically.

        :param class_name: Name of the class you want to create

        :param property_name: Name of the property to be used in the mixins.
                              'key' is used if not provided.

        :param mixin_imports: A list of class imports to add as base/mixins
                              e.g. [u'from classutils import Observable',]

        :param attributes: Dictionary of attributes in the dictionary.
                           Can also be a list of dictionaries.
                           Key: key into the dictionary
                           Values: {MANDATORY:  bool: True if the attribute
                                                is mandatory. Throws an
                                                exception if accessed and
                                                not found.
                                    PROPERTY: Name of the property to be
                                              associated with the attribute.
                                              e.g the key could be 'w', but
                                              a property name of 'width' is
                                              preferred.
                                    PROPERTIES: Make multiple properties for
                                                the same attribute. Useful if
                                                you want the original and a
                                                verbose version. e.g. 'w' and
                                                'width'
                                    DEFAULT: The default value for an optional
                                             attribute. If not supplied, None
                                             is used.

        :param key: Supply if you want to create parent mixins. It's the key
                    into the dictionary in the parent dict that contains
                    the bit of the response we're making classes for

        :param parent_mixin_imports: A list of class imports to add as base/mixins
                                     to the parent.
                                     e.g. [u'from classutils import Observable',]

        Example:
            JsonApiPropertiesClassCreator(class_name=u'Rectangle',
                                   key=u'rectangle',
                                   property_name=u'rect',
                                   attributes={u'w': {MANDATORY:  True,
                                                      PROPERTIES: [u'w', u'width'],},

                                                u'h': {MANDATORY:  True,
                                                       PROPERTIES: [u'h', u'height'],},

                                                u'col': {MANDATORY:  False,
                                                         PROPERTIES: [u'color', u'colour'],},

                                                u'border': {MANDATORY: False,
                                                            PROPERTY: u'border',
                                                            DEFAULT: 1},
                                                })

        Example generates the following code:

            # Code generated by classutils.JsonApiPropertiesClassCreator

            from classutils import JsonApiPropertiesClass


            class Rectangle(JsonApiPropertiesClass):

                def __init__(self,
                             *args,
                             **kwargs):
                    super(Rectangle, self).__init__(*args, **kwargs)

                @property
                def h(self):
                    return self.mandatory(u'h')

                @property
                def height(self):
                    return self.mandatory(u'h')

                @property
                def border(self):
                    return self.optional(u'border', 1)

                @property
                def color(self):
                    return self.optional(u'col')

                @property
                def colour(self):
                    return self.optional(u'col')

                @property
                def w(self):
                    return self.mandatory(u'w')

                @property
                def width(self):
                    return self.mandatory(u'w')


            class RectMandatoryMixIn(object):

                RECTANGLE = Rectangle  # Override in subclass if required

                def __init__(self):
                    super(RectMandatoryMixIn, self).__init__()

                @property
                def rect(self):
                    try:
                        return self._rect
                    except AttributeError:
                        pass
                    attribute = self.mandatory(u'rectangle')
                    if isinstance(attribute, list):
                        self._rect = [
                            Rectangle(
                                response=response,
                                parent=self)
                            for response in attribute]
                    elif isinstance(attribute, dict):
                        self._rect = Rectangle(
                            response=attribute,
                            parent=self)
                    else:
                        self._rect = None
                    return self._rect


            class RectOptionalMixIn(object):

                RECTANGLE = Rectangle  # Override in subclass if required

                def __init__(self):
                    super(RectOptionalMixIn, self).__init__()

                @property
                def rect(self):
                    try:
                        return self._rect
                    except AttributeError:
                        pass
                    attribute = self.optional(u'rectangle')
                    if isinstance(attribute, list):
                        self._rect = [
                            Rectangle(
                                response=response,
                                parent=self)
                            for response in attribute]
                    elif isinstance(attribute, dict):
                        self._rect = Rectangle(
                            response=attribute,
                            parent=self)
                    else:
                        self._rect = None
                    return self._rect
        """
        self.class_name = class_name
        if isinstance(attributes, (list, tuple)):
            self.attributes = {}
            for attribute in attributes:
                self.attributes.update(attribute)
        else:
            self.attributes = attributes if attributes else []
        self.key = key
        self.property_name = property_name
        self.imports = mixin_imports if mixin_imports else []
        self.mixins = [import_string.strip().split(u' ')[-1] for import_string in self.imports]
        self.parent_imports = parent_mixin_imports if parent_mixin_imports else []
        self.parent_mixins = [import_string.strip().split(u' ')[-1] for import_string in self.parent_imports]

    @property
    def base_class_name(self):
        return self.class_name if not self.mixins else u'{c}Base'.format(c=self.class_name)

    @property
    def filename(self):
        return u'{filename}.py'.format(filename=(self.property_name
                                                 if self.property_name
                                                 else self.class_name)).lower()

    def settings(self,
                 attribute):
        return self.attributes[attribute]

    def attribute_properties(self,
                             attribute):
        settings = self.attributes[attribute]
        return settings.get(self.PROPERTIES, [settings.get(self.PROPERTY, attribute)])

    @staticmethod
    def mandatory_or_optional(mandatory):
        return (u'mandatory'
                if mandatory
                else u'optional')

    def mandatory_or_optional_attribute(self,
                                        attribute):
        return self.mandatory_or_optional(self.settings(attribute).get(self.MANDATORY, False))

    def attribute_conversion(self,
                             attribute):
        attribute_conversion = self.settings(attribute).get(self.TYPE)
        if attribute_conversion and not isinstance(attribute_conversion, basestring):
            attribute_conversion = attribute_conversion.__name__
        return attribute_conversion


    def attribute_default(self,
                          attribute):
        default = self.settings(attribute).get(self.DEFAULT)
        if default is None:
            return u")"
        elif isinstance(default, basestring):
            return u", u'{d}')".format(d=default)  # TODO: Escape this
        else:
            return u', {d})'.format(d=default)

    @property
    def dictionary_response_class_code(self):

        class_code = [u'',
                      u'class {c_name}(JsonApiPropertiesClass):'.format(c_name=self.base_class_name),
                      u'',
                      u'    def __init__(self,',
                      u'                 *args,',
                      u'                 **kwargs):',
                      u'        super({c_name}, self).__init__(*args, **kwargs)'.format(c_name=self.base_class_name),
                      u'']

        for attribute in self.attributes:

            for property_name in self.attribute_properties(attribute):

                getter = (u"self.{mandatory_or_optional}(u'{f_name}'{default}"
                          .format(mandatory_or_optional=self.mandatory_or_optional_attribute(attribute),
                                  f_name=attribute,
                                  default=self.attribute_default(attribute)))

                if self.attribute_conversion(attribute):
                    getter = (u'{conversion}({getter})'
                              .format(conversion=self.attribute_conversion(attribute),
                                      getter=getter))

                property_code = [u'    @property',
                                 u'    def {p_name}(self):'.format(p_name=property_name),
                                 u'        return {getter}'.format(getter = getter),
                                 u'']
                class_code.extend(property_code)

        return class_code

    @property
    def augmented_class_code(self):
        class_code = []
        if self.mixins:
            indent = u' ' * len(u'class {class_name}('.format(class_name=self.class_name))
            mixins = [u'{indent}{mixin},'.format(indent=indent,
                                                 mixin=mixin)
                      for mixin in self.mixins]
            mixins[-1] = mixins[-1][:-1] + u'):'
            class_code.extend([u'',
                               u'class {class_name}({base_class_name},'
                               .format(class_name=self.class_name,
                                       base_class_name=self.base_class_name)])
            class_code.extend(mixins)
            class_code.extend([u'    pass  # Does this need an init?',
                               u''])
        return class_code

    def accessor_mix_in_code(self,
                             mandatory):

        mandatory_or_optional = self.mandatory_or_optional(mandatory)
        property_name = self.property_name if self.property_name else self.key
        mixin_name = u'{property_name}{m_or_o}MixIn'.format(property_name=property_name.capitalize(),
                                                            m_or_o=mandatory_or_optional.capitalize())
        if self.parent_mixins:
             indent = u',\n' + u' ' * len(u'class {mixin_name}('.format(mixin_name=mixin_name))
             parent_mixins = indent.join(self.parent_mixins)
        else:
             parent_mixins = u'object'

        return [u"",
                u"class {mixin_name}({parent_mixins}):".format(mixin_name = mixin_name,
                                                               parent_mixins = parent_mixins),
                u'',
                u'    {CLASS_NAME} = {class_name}  # Override in subclass if required'
                    .format(CLASS_NAME=self.class_name.upper(),
                            class_name=self.class_name),
                u'',
                u"    def __init__(self):",
                u"        super({mixin_name}, self).__init__()".format(mixin_name = mixin_name),
                u"",
                u"    @property",
                u"    def {p}(self):".format(p = property_name),
                u"        try:",
                u"            return self._{p}".format(p = property_name),
                u"        except AttributeError:",
                u"            pass",
                u"        attribute = self.{m_or_o}(u'{key}')".format(m_or_o=mandatory_or_optional,
                                                                      key=self.key),
                u"        if isinstance(attribute, list):",
                u"            self._{p} = [".format(p = property_name),
                u"                {class_name}(".format(class_name = self.class_name),
                u"                    response=response,",
                u"                    parent=self)",
                u"                for response in attribute]",
                u"        elif isinstance(attribute, dict):",
                u"            self._{p} = {class_name}(".format(p = property_name,
                                                                class_name = self.class_name),
                u"                response=attribute,",
                u"                parent=self)",
                u"        else:",
                u"            self._{p} = None".format(p = property_name),
                u"        return self._{p}".format(p = property_name),
                u""]

    @property
    def code(self):
        code = [u'# Code generated by classutils.responses.JsonApiPropertiesClassCreator',
                u'',
                u'from classutils import JsonApiPropertiesClass']
        code.extend(self.imports)
        code.extend(self.parent_imports)
        code.append(u'')
        code.extend(self.dictionary_response_class_code)

        if self.mixins:
            code.extend(self.augmented_class_code)

        if self.key:
            code.extend(self.accessor_mix_in_code(mandatory=True))
            code.extend(self.accessor_mix_in_code(mandatory=False))

        return u'\n'.join(code)

    def write_source_code(self,
                          filename=None,
                          output_filepath=None):
        filename = filename if filename else self.filename
        if not filename.endswith(u'.py'):
            filename += u'.py'
        path = (output_filepath
                if output_filepath
                else os.getcwd())
        file_path = os.path.join(path, filename)
        with open(file_path, mode=u'w') as of:
            of.write(self.code)
