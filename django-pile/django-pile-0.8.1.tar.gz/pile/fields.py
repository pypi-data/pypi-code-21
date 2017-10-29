
import sys

from PIL import Image

from django.db.models.fields import SmallIntegerField
from django.forms.fields import BooleanField
from django.forms.widgets import CheckboxInput, SplitDateTimeWidget

from django.db import models
from django.db.models import Field, OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.core.files.base import ContentFile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ('BooleanIntField','AutoOneToOneField','ResizedImageField',"BinaryField")

def int_test(value):
    return value == 1 or value is True

class IntCheckboxInput(CheckboxInput):
    def __init__(self, *args, **kwargs):
        CheckboxInput.__init__(self, *args, **kwargs)
        # This is needed to be able to save the value in the not checked state
        self.check_test = int_test

class BooleanIntFormField(BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = IntCheckboxInput
        BooleanField.__init__(self, *args, **kwargs)

    def clean(self, value):
        # This is needed to stop ValueRequired when unchecked
        return value and 1 or 0

class BooleanIntField(SmallIntegerField):
    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = BooleanIntFormField
        return SmallIntegerField.formfield(self, *args, **kwargs)

# This patched function might not make sense for mysql or postgres
def monkey_decompress(self, value):
    if isinstance(value, basestring):
        from dateutil import parser as any_date
        value = any_date.parse(value)
    return self._decompress(value)

SplitDateTimeWidget._decompress = SplitDateTimeWidget.decompress
SplitDateTimeWidget.decompress = monkey_decompress

class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)


class AutoOneToOneField(OneToOneField):
    '''
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.

    example:

        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            home_page = models.URLField(max_length=255, blank=True)
            icq = models.IntegerField(max_length=255, null=True)
    '''
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))


def _update_ext(filename, new_ext):
    parts = filename.split('.')
    parts[-1] = new_ext
    return '.'.join(parts)


class ResizedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        new_content = StringIO()
        content.file.seek(0)

        img = Image.open(content.file)
        # In-place optional resize down to propotionate size
        img.thumbnail(self.field.maximum, Image.ANTIALIAS)

        if img.size[0] < self.field.minimum[0] or \
           img.size[1] < self.field.minimum[1]:
            ret = img.resize(self.field.minimum, Image.ANTIALIAS)
            img.im   = ret.im
            img.mode = ret.mode
            img.size = self.field.minimum

        img.save(new_content, format=self.field.format)

        new_content = ContentFile(new_content.getvalue())
        new_name = _update_ext(name, self.field.format.lower())

        super(ResizedImageFieldFile, self).save(new_name, new_content, save)


class ResizedImageField(ImageField):
    """
    Saves only a resized version of the image file. There are two possible transformations:

     - Image is too big, it will be proportionally resized to fit the bounds.
     - Image is too small, it will be resized with distortion to fit.

    """
    attr_class = ResizedImageFieldFile

    def deconstruct(self):
        name, path, args, kwargs = super(ResizedImageField, self).deconstruct()
        for arg in ('min_width', 'max_width',
                    'min_height', 'max_height', 'format'):
            kwargs[arg] = getattr(self, arg)
        return name, path, args, kwargs

    def __init__(self, verbose_name=None,
             max_width=100, max_height=100,
             min_width=0, min_height=0,
             format='PNG', *args, **kwargs):
        self.minimum = (min_width, min_height)
        self.maximum = (max_width, max_height)
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.format = format
        super(ResizedImageField, self).__init__(verbose_name, *args, **kwargs)


class BinaryField(Field):
    """BinaryField brought back from django 1.7 - REMOVE ME when using newer django"""
    description = "Raw binary data"
    empty_values = [None, b'']

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return "BinaryField"

    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super(BinaryField, self).get_default()
        if default == '':
            return b''
        return default

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(BinaryField, self).get_db_prep_value(value, connection, prepared)
        if value is not None:
            return connection.Database.Binary(value)
        return value

    def value_to_string(self, obj):
        """Binary data is serialized as base64"""
        return b64encode(force_bytes(self._get_val_from_obj(obj))).decode('ascii')

    def to_python(self, value):
        # If it's a string, it should be base64-encoded data
        if isinstance(value, six.text_type):
            return six.memoryview(b64decode(force_bytes(value)))
        return value

