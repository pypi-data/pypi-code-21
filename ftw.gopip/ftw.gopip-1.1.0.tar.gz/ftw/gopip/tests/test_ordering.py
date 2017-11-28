from ftw.builder import Builder
from ftw.builder import create
from ftw.gopip.tests import FunctionalTestCase
from operator import attrgetter
from plone.folder.interfaces import IExplicitOrdering
from Products.CMFCore.utils import getToolByName


class TestOrdering(FunctionalTestCase):
    """Make sure that we do not break Plone standard behavior.
    """

    def test_plone_site_ordering(self):
        self.grant('Manager')
        create(Builder('folder').titled(u'two'))
        create(Builder('folder').titled(u'three'))
        create(Builder('page').titled(u'one'))
        self.assert_order('two', 'three', 'one')
        self.portal.moveObjectsByDelta(['one', 'two', 'three'],
                                       -len(self.portal.objectIds()))
        self.portal.plone_utils.reindexOnReorder(self.portal)
        self.assert_order('one', 'two', 'three')

    def test_folder_reorder_with_method(self):
        self.grant('Manager')
        folder = create(Builder('folder'))
        create(Builder('folder').titled(u'two').within(folder))
        create(Builder('folder').titled(u'three').within(folder))
        create(Builder('page').titled(u'one').within(folder))
        self.assert_order('two', 'three', 'one', 'folder')
        folder.moveObjectsByDelta(['one', 'two', 'three'], -3)
        self.assert_order('one', 'two', 'three', 'folder')

    def test_folder_reorder_with_adapter(self):
        self.grant('Manager')
        folder = create(Builder('folder'))
        create(Builder('folder').titled(u'two').within(folder))
        create(Builder('folder').titled(u'three').within(folder))
        create(Builder('page').titled(u'one').within(folder))
        self.assert_order('two', 'three', 'one', 'folder')
        IExplicitOrdering(folder).moveObjectsByDelta(['one', 'two', 'three'], -3)
        self.assert_order('one', 'two', 'three', 'folder')

    def assert_order(self, *expected_ordered_ids):
        catalog = getToolByName(self.portal, 'portal_catalog')
        brains = catalog({'sort_on': 'getObjPositionInParent'})
        got_ordered_ids = tuple(map(attrgetter('getId'), brains))
        self.assertEquals(expected_ordered_ids, got_ordered_ids)
