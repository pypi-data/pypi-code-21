import flask
import pytest

from manhattan.nav import LazyNavItem, NavItem


def test_init():
    """Initialize a `NavItemLazy` instance"""

    def foo(creator):
        return [NavItem('Foo', 'foo')]

    lazy_item = LazyNavItem(foo, 'bar')

    assert lazy_item.func is foo
    assert lazy_item.after is 'bar'

def test_items():
    """Generate the nav items for a `LazyNavItem`"""

    def foo(creator):
        return [NavItem('Foo', 'foo')]

    lazy_item = LazyNavItem(foo)

    assert lazy_item.items[0].label == 'Foo'
    assert lazy_item.items[0].endpoint == 'foo'

def test_parent():
    """Return the parent for a `LazyNavItem`"""

    def foo(creator):
        return [NavItem('Foo', 'foo')]

    lazy_item = LazyNavItem(foo)

    bar = NavItem()
    bar.add(lazy_item)

    assert lazy_item.parent == bar