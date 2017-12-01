import flask
import pytest

from manhattan.nav import LazyNavItem, NavItem
from . import app


def test_init():
    """Initialize a `NavItem` instance"""

    def badge():
        return True

    # Initialize with no options (as a root item)(
    item = NavItem()

    assert item.label == None
    assert item.endpoint == None
    assert item._view_args == {}
    assert item.fixed_url == None
    assert item.id == None
    assert item._badge == None
    assert item._data == {}
    assert item.after == None

    # Initialized as a typical endpoint/view_args nav
    item = NavItem(
        label='Foo',
        endpoint='foo',
        view_args={'foo': 'bar'},
        badge=badge,
        data={'foo': 'bar'},
        after='bar'
        )

    assert item.label == 'Foo'
    assert item.endpoint == 'foo'
    assert item._view_args == {'foo': 'bar'}
    assert item.fixed_url == None
    assert item.id == 'foo'
    assert item._badge is badge
    assert item._data == {'foo': 'bar'}
    assert item.after == 'bar'

    # Initialized as a fixed URL
    item = NavItem(
        label='Foo',
        fixed_url='http://www.example.com',
        id='foo',
        badge=badge,
        data={'foo': 'bar'},
        after='bar'
        )

    assert item.label == 'Foo'
    assert item.endpoint == None
    assert item._view_args == {}
    assert item.fixed_url == 'http://www.example.com'
    assert item.id == 'foo'
    assert item._badge is badge
    assert item._data == {'foo': 'bar'}
    assert item.after == 'bar'

def test_badge():
    """Return the output of the badge property called"""

    def badge():
        return 99

    # Check if no badge is defined we get None back
    item = NavItem()
    assert item.badge == None

    # Check if badge is set to a non-callable value we get that back
    item.badge = True
    assert item.badge is True

    # Check if badge is a callable we get back the output of calling it
    item.badge = badge
    assert item.badge == 99

def test_children():
    """
    Return the children for a nav order based on any `after` argument of each
    item and expanding any `LazyNavItem` instances.
    """

    # Build a fake navigation menu
    menu = NavItem()
    menu.add(NavItem('Item 1', 'item.1'))
    sub_menu = menu.add(NavItem('Item 2', 'item.2'))
    sub_menu.add(NavItem('Sub-Item 1', 'sub_item.1'))
    sub_menu.add(NavItem('Sub-Item 2', 'sub_item.2'))
    lazy_menu = menu.add(NavItem('Lazy', 'lazy', after='item.1'))

    def build_lazy_nav(lazy_nav_item):
        items = []
        for i in range(1, 4):
            items.append(NavItem('Lazy ' + str(i), 'lazy.' + str(i)))
        return items

    lazy_menu.add(LazyNavItem(build_lazy_nav))

    menu_items = menu.children
    lazy_menu_items = lazy_menu.children
    sub_menu_items = sub_menu.children

    # Check the output of the menu and sub-menus are correct
    assert menu_items[0].label == 'Item 1'
    assert menu_items[1].label == 'Lazy'
    assert menu_items[2].label == 'Item 2'

    assert lazy_menu_items[0].label == 'Lazy 1'
    assert lazy_menu_items[1].label == 'Lazy 2'
    assert lazy_menu_items[2].label == 'Lazy 3'

    assert sub_menu_items[0].label == 'Sub-Item 1'
    assert sub_menu_items[1].label == 'Sub-Item 2'


def test_data():
    """
    Return the data for the `NavItem` which can be either the value assigned to
    it or the output of the value if it is callable.
    """

    def data():
        return {'bar': 'zee'}

    # Check if no data is defined we get None back
    item = NavItem()
    assert item.data == {}

    # Check if data is set to a non-callable value we get that back
    item.data = {'foo': 'bar'}
    assert item.data == {'foo': 'bar'}

    # Check if data is a callable we get back the output of calling it
    item.data = data
    assert item.data == {'bar': 'zee'}

def test_is_active(app):
    """Return True if the nav item is active"""

    with app.test_client() as client:
        client.get('/')
        item = NavItem('Sub', 'sub_view')
        assert not item.is_active

        client.get('/sub')
        item = NavItem('Sub', 'sub_view')
        assert item.is_active

        client.get('/sub/sub')
        item = NavItem('Sub', 'sub_view')
        assert item.is_active

def test_is_open(app):
    """
    Return True if the nav item is active or has an active child and therefore
    should be open.
    """

    with app.test_client() as client:
        client.get('/')
        item = NavItem('Sub', 'sub_view')
        assert not item.is_open

        client.get('/sub')
        item = NavItem('Sub', 'sub_view')
        assert item.is_open

        client.get('/sub/sub')
        item = NavItem('Sub')
        child = item.add(NavItem('Sub child', 'sub_view'))
        assert item.is_open

def test_is_parent():
    """Return True it the `NavItem` has children"""

    # Check that if an item has no children `is_parent` is false
    item = NavItem()
    assert item.is_parent == False

    # Check if we add a child to our item it is now flagged a parent
    item.add(NavItem())
    assert item.is_parent == True

def test_parent():
    """Return the parent for a `NavItem`"""
    item = NavItem()
    sub_item = item.add(NavItem())
    assert sub_item.parent == item

def test_query(app):
    """Return the query for the given `NavItem`"""

    item = NavItem('Protected', 'protected_view', {'allowed': 'yep'})
    link = item.query
    assert link.exists == True
    assert link.allowed == True
    assert link.active == False
    assert link.url == '/protected/yep'

def test_view_args():
    """
    Return the view arguments for the `NavItem` which can be either the
    dictionary assigned to it or the output of the an assigned callable.
    """

    def view_args():
        return {'bar': 'zee'}

    # Check if no view args is defined we get None back
    item = NavItem()
    assert item.view_args == {}

    # Check if view args is set to a non-callable value we get that back
    item.view_args = {'foo': 'bar'}
    assert item.view_args == {'foo': 'bar'}

    # Check if view args is a callable we get back the output of calling it
    item.view_args = view_args
    assert item.view_args == {'bar': 'zee'}

def test_add():
    """Add a `NavItem` or `LazyNavItem` as a child of this `NavItem`."""
    item = NavItem()

    # Check that we can add a `NavItem`
    sub_item = NavItem()
    item.add(sub_item)
    assert item._children[0] is sub_item

    # Check that we can add a `LazyNavItem`
    lazy_item = LazyNavItem(lambda creator: [])
    item.add(lazy_item)
    assert item._children[1] is lazy_item

    # Check that we can add a nav item at a given index
    indexed_item = NavItem()
    item.add(indexed_item, index=0)
    assert item._children[0] is indexed_item

