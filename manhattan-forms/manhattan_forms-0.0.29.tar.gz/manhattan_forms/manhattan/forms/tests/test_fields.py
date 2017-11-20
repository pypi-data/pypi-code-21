from datetime import date, time

from mongoframes import *
import pytest
from werkzeug.datastructures import MultiDict

from manhattan.forms import BaseForm
from manhattan.forms import fields

from .frames import Dragon


def test_checkbox_field():
    """Support for multiple checkboxes"""

    class MyForm(BaseForm):

        foo = fields.CheckboxField(
            'Foo',
            choices=[
                ('bar', 'Bar'),
                ('zee', 'Zee'),
                ('omm', 'Omm')
                ]
            )

    # Check a valid selections are supported
    form = MyForm(MultiDict({'foo': ['bar', 'zee', 'omm']}))
    assert form.validate() == True
    assert form.data['foo'] == ['bar', 'zee', 'omm']

    # Check invalid selections raise an error
    form = MyForm(MultiDict({'foo': ['one', 'zee', 'omm']}))
    assert form.validate() == False
    assert form.errors['foo'][0] == "'one' is not a valid choice for this field"

def test_date_field():
    """A date field that supports setting the default date format"""

    class MyForm(BaseForm):

        foo = fields.DateField('Foo')

    # Check the default format is as expected
    form = MyForm()
    assert form.foo.format == '%Y-%m-%d'

    # Modify the default format to a string and check the default is as expected
    fields.DateField.default_format = '%d/%m/%Y'
    form = MyForm()
    assert form.foo.format == '%d/%m/%Y'

    # Modify the default format to a function and check the default is as
    # expected.
    fields.DateField.default_format = lambda: '%d.%m.%Y'
    form = MyForm()
    assert form.foo.format == '%d.%m.%Y'

    # Check we cans still override the default

    class MyForm(BaseForm):

        foo = fields.DateField('Foo', format='%d-%m-%Y')

    form = MyForm()
    assert form.foo.format == '%d-%m-%Y'

    # Check that the dash qualifier in the format string is stripped when
    # parsing.

    class MyForm(BaseForm):

        foo = fields.DateField('Foo', format='%-d %B %Y')

    form = MyForm(MultiDict({'foo': '1 January 2000'}))
    assert form.validate() == True
    assert form.data['foo'] == date(2000, 1, 1)

def test_document_checkboxes_field(dragons):
    """
    Support for multiple checkboxes generated from documents in the database.
    """

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.DocumentCheckboxField(
            'Foo',
            frame_cls=Dragon,
            filter=Q.breed == 'Fire-drake',
            sort=[('name', ASC)]
            )

    my_form = MyForm()
    choices = [
        (d._id, str(d)) for d in
        Dragon.many(Q.breed == 'Fire-drake', sort=[('name', ASC)])
        ]
    assert my_form.foo.choices == choices

    # Check setting id and label attributes
    class MyForm(MyForm):
        foo = fields.DocumentCheckboxField(
            'Foo',
            frame_cls=Dragon,
            id_attr='name',
            label_attr='breed',
            sort=[('name', ASC)]
            )

    my_form = MyForm()
    choices = [(d.name, d.breed) for d in Dragon.many(sort=[('name', ASC)])]
    assert my_form.foo.choices == choices

    # Check setting a projection
    class MyForm(MyForm):
        foo = fields.DocumentCheckboxField(
            'Foo',
            frame_cls=Dragon,
            label_attr='breed',
            sort=[('name', ASC)],
            projection={'name': True}
            )

    my_form = MyForm()
    choices = [(d._id, None) for d in Dragon.many(sort=[('name', ASC)])]
    assert my_form.foo.choices == choices

    # Check setting a filter as a lambda argument
    class MyForm(BaseForm):
        foo = fields.DocumentCheckboxField(
            'Foo',
            frame_cls=Dragon,
            filter=lambda form, field: Q.breed == 'Fire-drake',
            sort=[('name', ASC)]
            )

    my_form = MyForm()
    choices = [
        (d._id, str(d)) for d in
        Dragon.many(Q.breed == 'Fire-drake', sort=[('name', ASC)])
        ]
    assert my_form.foo.choices == choices

    # Check setting a limit
    class MyForm(MyForm):
        foo = fields.DocumentCheckboxField(
            'Foo',
            frame_cls=Dragon,
            label_attr='name',
            sort=[('name', ASC)],
            limit=2
            )

    my_form = MyForm()
    choices = [
        (d._id, d.name) for d in Dragon.many(sort=[('name', ASC)], limit=2)]
    assert my_form.foo.choices == choices

def test_document_select_field(dragons):
    """
    Support for select field generated from documents in the database.
    """

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            filter=Q.breed == 'Fire-drake',
            sort=[('name', ASC)]
            )

    empty_option = ('', 'Select...')

    my_form = MyForm()
    choices = [
        (d._id, str(d)) for d in
        Dragon.many(Q.breed == 'Fire-drake', sort=[('name', ASC)])
        ]
    choices.insert(0, empty_option)
    assert my_form.foo.choices == choices

    # Check setting id and label attributes
    class MyForm(MyForm):
        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            id_attr='name',
            label_attr='breed',
            sort=[('name', ASC)]
            )

    my_form = MyForm()
    choices = [(d.name, d.breed) for d in Dragon.many(sort=[('name', ASC)])]
    choices.insert(0, empty_option)
    assert my_form.foo.choices == choices

    # Check setting a projection
    class MyForm(MyForm):
        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            label_attr='breed',
            sort=[('name', ASC)],
            projection={'name': True}
            )

    my_form = MyForm()
    choices = [(d._id, None) for d in Dragon.many(sort=[('name', ASC)])]
    choices.insert(0, empty_option)
    assert my_form.foo.choices == choices

    # Check setting a filter as a lambda argument
    class MyForm(BaseForm):
        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            filter=lambda form, field: Q.breed == 'Fire-drake',
            sort=[('name', ASC)]
            )

    my_form = MyForm()
    choices = [
        (d._id, str(d)) for d in
        Dragon.many(Q.breed == 'Fire-drake', sort=[('name', ASC)])
        ]
    choices.insert(0, empty_option)
    assert my_form.foo.choices == choices

    # Check setting a limit
    class MyForm(MyForm):
        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            label_attr='name',
            sort=[('name', ASC)],
            limit=2
            )

    my_form = MyForm()
    choices = [
        (d._id, d.name) for d in Dragon.many(sort=[('name', ASC)], limit=2)]
    choices.insert(0, empty_option)
    assert my_form.foo.choices == choices

    # Check setting without empty option
    class MyForm(MyForm):
        foo = fields.DocumentSelectField(
            'Foo',
            frame_cls=Dragon,
            filter=Q.breed == 'Fire-drake',
            sort=[('name', ASC)],
            empty_label=None
            )

    my_form = MyForm()
    choices = [
        (d._id, str(d)) for d in
        Dragon.many(Q.breed == 'Fire-drake', sort=[('name', ASC)])
        ]
    assert my_form.foo.choices == choices

def test_price_field():
    """Accept a price"""

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.PriceField('Foo')

    # Check that populating the form
    my_form = MyForm(foo=1000)
    assert my_form.foo._value() == '10.00'

    # Check various different price formats
    my_form = MyForm(MultiDict({'foo': '10'}))
    assert my_form.data['foo'] == 1000

    my_form = MyForm(MultiDict({'foo': '.1'}))
    assert my_form.data['foo'] == 10

    my_form = MyForm(MultiDict({'foo': '1.1'}))
    assert my_form.data['foo'] == 110

    my_form = MyForm(MultiDict({'foo': '10.01'}))
    assert my_form.data['foo'] == 1001

    # Check setting denomination units
    class MyForm(BaseForm):
        foo = fields.PriceField('Foo', denomination_units=1)

    my_form = MyForm(MultiDict({'foo': '10.01'}))
    assert my_form.data['foo'] == 10

    # Check setting coerce
    class MyForm(BaseForm):
        foo = fields.PriceField('Foo', denomination_units=1, coerce=float)

    my_form = MyForm(MultiDict({'foo': '10.01'}))
    assert my_form.data['foo'] == 10.01

def test_slug_field():
    """Accept a valid slug or build one if none is provided"""

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        bar = fields.StringField('Bar')
        foo = fields.SlugField('Foo', template='{bar}')

    # Accepts a valid slug
    my_form = MyForm(MultiDict({'foo': 'test-slug'}))
    assert my_form.validate() == True
    assert my_form.data['foo'] == 'test-slug'

    # Provides a valid slug through a template string
    my_form = MyForm(MultiDict({'bar': 'test slug', 'foo': ''}))
    assert my_form.validate() == True
    assert my_form.data['foo'] == 'test-slug'

    # Check invalid slugs raise an error
    my_form = MyForm(MultiDict({'bar': 'test slug', 'foo': 'test / test'}))
    assert my_form.validate() == False

    error = my_form.errors['foo'][0]
    assert str(error) == \
            "Not a valid slug. (Use a-z, 0-1 and '-' characters only)"
    assert error.suggestion == 'test-slug'

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        bar = fields.StringField('Bar')
        foo = fields.SlugField('Foo', template='{bar}', allow_paths=True)

    # Accepts a valid path
    my_form = MyForm(MultiDict({'foo': 'test/slug'}))
    assert my_form.validate() == True
    assert my_form.data['foo'] == 'test/slug'

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        bar = fields.StringField('Bar')
        foo = fields.SlugField('Foo', template=lambda d: d['bar'] + ' bar')

    # Provides a valid slug through a callable template
    my_form = MyForm(MultiDict({'bar': 'test slug', 'foo': ''}))
    assert my_form.data['foo'] == 'test-slug-bar'

def test_string_list_field():
    """Accept a list defined as a string"""

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.StringListField('Foo')

    my_form = MyForm(MultiDict({'foo': 'bar\nzee\nZee\n\nomm'}))
    assert my_form.data['foo'] == ['bar', 'zee', 'omm']

    # Check setting a separator
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', separator=',')

    my_form = MyForm(MultiDict({'foo': 'bar,zee,omm'}))
    assert my_form.data['foo'] == ['bar', 'zee', 'omm']

    # Check setting removing blanks
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', remove_blanks=False)

    my_form = MyForm(MultiDict({'foo': 'bar\nzee\n\nomm'}))
    assert my_form.data['foo'] == ['bar', 'zee', '', 'omm']

    # Check setting removing duplicates
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', remove_duplicates=False)

    my_form = MyForm(MultiDict({'foo': 'bar\nzee\nzee\nomm'}))
    assert my_form.data['foo'] == ['bar', 'zee', 'zee', 'omm']

    # Check setting case sensitivity
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', case_sensitive=True)

    my_form = MyForm(MultiDict({'foo': 'bar\nzee\nZee\nomm'}))
    assert my_form.data['foo'] == ['bar', 'zee', 'Zee', 'omm']

    # Check setting coerce
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', coerce=int)

    my_form = MyForm(MultiDict({'foo': '1\n2\n3'}))
    assert my_form.data['foo'] == [1, 2, 3]

    # Check setting sort
    class MyForm(BaseForm):
        foo = fields.StringListField('Foo', sort=True)

    my_form = MyForm(MultiDict({'foo': 'bar\nzee\nomm'}))
    assert my_form.data['foo'] == ['bar', 'omm', 'zee']

def test_time_field():
    """Accept a valid time"""

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.TimeField('Foo')

    # Check valid times are accepted
    form = MyForm(MultiDict({'foo': '22:50'}))
    assert form.validate() == True
    assert form.data['foo'] == time(22, 50)

    # Check invalid times raise an error
    form = MyForm(MultiDict({'foo': 'Ten-fifty'}))
    assert form.validate() == False
    assert form.errors['foo'][0] == 'Not a valid time value.'

    # Check a custom format can be used to accept seconds
    class MyForm(BaseForm):
        foo = fields.TimeField('Foo', format='%H:%M:%S')

    form = MyForm(MultiDict({'foo': '22:50:55'}))
    assert form.validate() == True
    assert form.data['foo'] == time(22, 50, 55)

def test_yesno_field():
    """Test a field that accepts y, n and returns a bool"""

    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.YesNoField('Foo')

    # Check that y is accepted
    form = MyForm(MultiDict({'foo': 'y'}))
    assert form.validate() == True
    assert form.data['foo'] is True

    # Check that n is accepted
    form = MyForm(MultiDict({'foo': 'n'}))
    assert form.validate() == True
    assert form.data['foo'] is False

    # Check that bool values are correctly coerced to themselves e.g
    # True == True

    # Check that passing True sets the data to be True
    form = MyForm(MultiDict({'foo': True}))
    assert form.data['foo'] is True

    # Check that passing True sets the data to be True
    form = MyForm(MultiDict({'foo': False}))
    assert form.data['foo'] is False


    # Check that none value raises an input error
    form = MyForm(MultiDict({'foo': None}))
    assert form.validate() == False
    assert form.errors['foo'][0] == 'This field is required.'

    # Check that a field with the input validator removed does not error
    # on a none value
    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.YesNoField('Foo', validators=[])

    form = MyForm(MultiDict({'foo': None}))
    assert form.validate() == True

    # Check a custom set of choices and coerces works
    class MyForm(BaseForm):

        class Meta:
            csrf = False

        foo = fields.YesNoField(
            'Foo',
            choices=[('bar', 'Bar'), ('foo', 'Foo')],
            coerce=lambda x: {'bar': True, 'foo': False}.get(x, None)
            )

    form = MyForm(MultiDict({'foo': 'bar'}))
    assert form.validate() == True
    assert form.data['foo'] is True

    # Check that n is accepted
    form = MyForm(MultiDict({'foo': 'foo'}))
    assert form.validate() == True
    assert form.data['foo'] is False

    # Check that none value raises an input error
    form = MyForm(MultiDict({'foo': None}))
    assert form.validate() == False
    assert form.errors['foo'][0] == 'This field is required.'
