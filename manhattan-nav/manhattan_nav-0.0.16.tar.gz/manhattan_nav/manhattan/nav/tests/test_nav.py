import pytest

from manhattan.nav import MenuNotFound, Nav, NavItem
from . import app


def test_allowed(app):
    """
    Returns True if the caller is allowed to access a named endpoint and Talse
    if not.
    """
    with app.test_client() as client:
        assert Nav.allowed('protected_view', allowed='yep') is True
        assert Nav.allowed('protected_view', allowed='nope') is False

def test_apply():
    """Apply one of more rules to an endpoint"""
    rule_names = ['foo', 'bar']
    Nav.apply('protected_view', rule_names)
    assert Nav._endpoint_rules['protected_view'] == rule_names
    assert Nav._endpoint_rules['protected_view'] is not rule_names

def test_exists(app):
    """Return True if the named endpoint exists else return False"""
    with app.test_client() as client:
        assert Nav.exists('protected_view') is True
        assert Nav.exists('some_other_view') is False

def test_local_menu(app):
    """
    Return a local menu (a NavItem in reality).
    """
    menu = Nav.local_menu()

    # Check we get a `NavItem` back
    assert isinstance(menu, NavItem)

    # Check subsequent calls return a different NavItem instance.
    assert menu is not Nav.local_menu()

def test_menu(app):
    """
    Define and/or retrieve (if already defined) a nav menu (a NavItem in
    reality).
    """
    menu = Nav.menu('foo')

    # Check we get a `NavItem` back
    assert isinstance(menu, NavItem)

    # Check subsequent calls with the same name returns the same NavItem
    # instance.
    assert menu is Nav.menu('foo')

    # Check that attempting to fetch a menu that doesn't exist with the
    # `raise_unless_exists` flag set to `True` raises a `MenuNotFound`
    # exception.
    with pytest.raises(MenuNotFound):
        assert menu is Nav.menu('bar', raise_unless_exists=True)

def test_query(app):
    """
    Query endpoints (with view arguments) to see if;

    - the endpoint exist,
    - we are allowed to call the endpoint with the given view arguments
    - and if the endpoint with the given view arguments is the active request.

    The query should also include the URL for the endpoint and view args.
    """

    with app.test_client() as client:

        client.get('/')

        # Non-existant query
        link = Nav.query('some_other_view')
        assert link.exists == False
        assert link.allowed == False
        assert link.active == False
        assert link.active_sub == False
        assert link.url == None

        # A view that is also the current request path
        link = Nav.query('view')
        assert link.exists == True
        assert link.allowed == True
        assert link.active == True
        assert link.active_sub == False
        assert link.url == '/'

        # A protected view we can access that isn't the active request
        link = Nav.query('protected_view', allowed='yep')
        assert link.exists == True
        assert link.allowed == True
        assert link.active == False
        assert link.active_sub == False
        assert link.url == '/protected/yep'

        # A view we cannot access
        link = Nav.query('protected_view', allowed='nope')
        assert link.exists == True
        assert link.allowed == False
        assert link.active == False
        assert link.active_sub == False
        assert link.url == '/protected/nope'

        # Sub-active
        link = Nav.query('sub_view')
        assert link.exists == True
        assert link.allowed == True
        assert link.active == False
        assert link.active_sub == False
        assert link.url == '/sub'

        client.get('/sub/sub')

        link = Nav.query('sub_view')
        assert link.exists == True
        assert link.allowed == True
        assert link.active == False
        assert link.active_sub == True
        assert link.url == '/sub'

        # Ignore params
        client.get('/?foo=bar')

        link = Nav.query('view')
        assert link.exists == True
        assert link.allowed == True
        assert link.active == True
        assert link.active_sub == False
        assert link.url == '/'

def test_rule(app):
    """Use the `Nav.rule` decorator to define a function as a rule"""

    # Check we can define a rule using the function's name
    @Nav.rule
    def foo(**kwargs):
        return False

    assert Nav._rules['foo'] is foo

    # Check we can define a rule using a custom name
    @Nav.rule(name='zee')
    def bar(**kwargs):
        return False

    assert Nav._rules['zee'] is bar

def test_set_rule(app):
    """Define a function as a rule"""

    # Check we can define a rule using the function's name
    def foo(**kwargs):
        return False
    Nav.set_rule(foo)

    assert Nav._rules['foo'] is foo

    # Check we can define a rule using a custom name
    def bar(**kwargs):
        return False
    Nav.set_rule(bar, name='zee')

    assert Nav._rules['zee'] is bar
