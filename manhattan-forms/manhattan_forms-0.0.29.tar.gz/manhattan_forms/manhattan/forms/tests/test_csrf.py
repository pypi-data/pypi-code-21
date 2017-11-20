import flask
import pytest

from manhattan.forms import CSRF


# Fixtures

@pytest.fixture
def app():
    # Create a test application to run
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'SECRET_KEY'
    app.config['CSRF_SECRET_KEY'] = 'CSRF_SECRET_KEY'

    # Add CSRF protection to the app
    CSRF.init_app(app)

    @app.route('/view', methods=['GET', 'POST'])
    def view():
        return 'view'

    @CSRF.exempt
    @app.route('/exempt-view', methods=['GET', 'POST'])
    def exempt_view():
        return 'view'

    # Create a blueprint
    my_blueprint = flask.Blueprint('my_blueprint', __name__)

    @my_blueprint.route('/blueprint-view', methods=['GET', 'POST'])
    def blueprint_view():
        return 'view'

    CSRF.exempt(my_blueprint)

    app.register_blueprint(my_blueprint)

    yield app


# Tests

def test_csrf_protection(app):
    """Check that CSRF protection can be initialized for the app"""
    with app.test_client() as client:

        # Check sending a token allows a protected view to be called
        token = CSRF.generate_token()
        res = client.post('/view', data={'csrf_token': token})
        res.status_code == 200

        # Check not sending token generates a bad request
        res = client.post('/view')
        assert res.status_code == 400

def test_exempt_blueprint(app):
    """Check that we can exempt a blueprint from CSRF protection"""
    with app.test_client() as client:
        res = client.post('/blueprint-view')
        assert res.status_code == 200

def test_exempt_view(app):
    """Check that we can exempt a view from CSRF protection"""
    with app.test_client() as client:
        res = client.post('/exempt-view')
        assert res.status_code == 200

def test_exempt_configure_methods(app):
    """Check that we can configure the methods that implement CSRF protection"""

    # Configure the app to CSRF protect GET methods only
    app.config['CSRF_METHODS'] = ['GET']

    with app.test_client() as client:
        # Check POSTing to the protect view is now allowed
        res = client.post('/blueprint-view')
        assert res.status_code == 200

        # Check we can't GET the protected view without a CSRF token
        res = client.get('/view')
        assert res.status_code == 400

        token = CSRF.generate_token()
        res = client.get('/view', data={'csrf_token': token})
        res.status_code == 200