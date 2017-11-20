import flask
import pytest
from wtforms.fields import StringField

from manhattan.forms import BaseForm


def test_base_form():
    """`BaseForm`s support for CSRF protection and whitespace stripping"""

    # Create a test form
    class MyForm(BaseForm):

        class Meta:
            csrf = True

        foo = StringField('Foo')

    # Create a test application to run
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'SECRET_KEY'
    app.config['CSRF_SECRET_KEY'] = 'CSRF_SECRET_KEY'

    # Check CSRF protection
    @app.route('/crsf', methods=['GET', 'POST'])
    def crsf():
        form = MyForm(flask.request.values)
        if flask.request.method == 'POST':
            if form.validate():
                return 'success'
            else:
                return 'failed'

        return form.csrf_token.current_token

    with app.test_client() as client:

        # Sending valid CSRF token
        token = client.get('/crsf').data
        res = client.post('/crsf', data={'csrf_token': token})
        assert res.data == b'success'

        # Sending invalid CSRF token
        token = client.get('/crsf').data
        res = client.post('/crsf', data={'csrf_token': str(token) + '_invalid'})
        assert res.data == b'failed'

    # Disable CSRF for the remaining tests (this also tests that we can disable
    # CSRF protection from the form).
    MyForm.Meta.csrf = False

    # Check whitespace stripping
    @app.route('/ws-strip', methods=['POST'])
    def ws_strip():
        form = MyForm(flask.request.values)
        if flask.request.method == 'POST':
            if form.validate():
                return form.data['foo']

    with app.test_client() as client:
        res = client.post('/ws-strip', data={'foo': ' space '})
        assert res.data == b'space'

    # Check whitespace stripping can be disabled
    MyForm.Meta.strip_input = False

    with app.test_client() as client:
        res = client.post('/ws-strip', data={'foo': ' space '})
        assert res.data == b' space '

def test_obj_property():
    """Return the `obj` passed to the form when initialized"""

    # Create a test form
    class MyForm(BaseForm):
        foo = StringField('Foo')

    # Initialize the form with a value for `obj`
    foo = {'bar': 'zee'}
    form = MyForm(obj=foo)

    # Check the `obj` property returns the same values as the form was
    # initialized with.
    assert form.obj == foo