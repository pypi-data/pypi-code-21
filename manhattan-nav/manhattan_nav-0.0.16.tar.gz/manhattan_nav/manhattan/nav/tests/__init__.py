import flask
import pytest

from manhattan.nav import Nav

__all__ = ['app']


@pytest.fixture
def app():
    # Create a test application to run
    app = flask.Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def view():
        return 'ok'

    @app.route('/sub', methods=['GET', 'POST'])
    def sub_view():
        return 'ok'

    @app.route('/sub/sub', methods=['GET', 'POST'])
    def sub_sub_view():
        return 'ok'

    @app.route('/protected/<path:allowed>', methods=['GET', 'POST'])
    def protected_view(allowed):
        return 'ok'

    @Nav.rule
    def protect(allowed=None):
        return allowed == 'yep'

    Nav.apply('protected_view', ['protect'])

    yield app