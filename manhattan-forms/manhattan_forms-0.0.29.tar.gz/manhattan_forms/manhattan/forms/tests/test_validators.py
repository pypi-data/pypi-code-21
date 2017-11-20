import flask
from mongoframes import *
import pytest
from werkzeug.datastructures import MultiDict
from wtforms.fields import StringField

from manhattan.forms import BaseForm
from manhattan.forms import validators

from .frames import Dragon


# Fixtures

@pytest.fixture
def app():
    # Create a test application to run
    app = flask.Flask(__name__)

    @app.route('/view', methods=['GET', 'POST'])
    def view():
        return 'view'

    yield app


# Tests

def test_required_if():
    """
    Flag a field as required if a given condition is met by one or more other
    fields.
    """

    class MyForm(BaseForm):

        foo = StringField('Foo')
        bar = StringField('Bar')
        zee = StringField(
            'Zee',
            validators=[validators.RequiredIf(foo='bar', bar='zee')]
            )

    # Check `zee` is required if conditions are met
    form = MyForm(MultiDict({'foo': 'bar'}))
    assert form.validate() == False
    assert form.errors['zee'][0] == 'This field is required.'

    form = MyForm(MultiDict({'foo': 'foo', 'bar': 'zee'}))
    assert form.validate() == False
    assert form.errors['zee'][0] == 'This field is required.'

    # Check `zee` is optional if conditions are not met
    form = MyForm(MultiDict({'foo': 'foo', 'bar': 'bar'}))
    assert form.validate() == True


def test_unique_document(app, dragons):
    """Require the value of a field to be unique within a set of documents"""

    # Dragon must have unique names (case sensitive)

    class MyForm(BaseForm):

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(Dragon)
                ])

    form = MyForm(MultiDict({'name': 'Burt'}))
    assert form.validate() == False

    error = form.errors['name'][0]
    assert str(error) == 'Another document exists with the same value'

    # Dragon must have unique names (case insensitive)

    class MyForm(BaseForm):

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(Dragon, case_sensitive=False)
                ])

    form = MyForm(MultiDict({'name': 'burt'}))
    assert form.validate() == False

    error = form.errors['name'][0]
    assert str(error) == 'Another document exists with the same value'

    # Check we can filter the unique document set (with a query)

    class MyForm(BaseForm):

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(Dragon, filter=Q.name != 'Burt')
                ])

    form = MyForm(MultiDict({'name': 'Burt'}))
    assert form.validate() == True

    # Check we can filter the unique document set (with a callable)

    class MyForm(BaseForm):

        existing_name = StringField('Existing name')

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(
                    Dragon,
                    filter=lambda form, field: Q.name != form.existing_name.data
                    )
                ])

    form = MyForm(MultiDict({'existing_name': 'Burt', 'name': 'Burt'}))
    assert form.validate() == True

    # Check an endpoint is provided to any matching document

    class MyForm(BaseForm):

        existing_name = StringField('Existing name')

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(
                    Dragon,
                    endpoint='view',
                    endpoint_args=lambda doc: {'dragon': doc.name}
                    )
                ])

    form = MyForm(MultiDict({'name': 'Burt'}))
    assert form.validate() == False

    error = form.errors['name'][0]
    assert error.matching_url == '/view?dragon=Burt'

    # Check an alternative is provided

    class MyForm(BaseForm):

        existing_name = StringField('Existing name')

        name = StringField(
            'Name',
            validators=[
                validators.UniqueDocument(
                    Dragon,
                    alternative=lambda v, i: '{v}-{i}'.format(v=v, i=i + 1)
                    )
                ])

    form = MyForm(MultiDict({'name': 'Burt'}))
    assert form.validate() == False

    error = form.errors['name'][0]
    assert error.alternative == 'Burt-1'