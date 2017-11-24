from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_traversal_types
from ftw.referencewidget.interfaces import IReferenceSettings
from ftw.referencewidget.testing import FTW_REFERENCE_FUNCTIONAL_TESTING
from ftw.referencewidget.tests.views.form import TestView
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility
import transaction


class TestFieldConverter(TestCase):
    layer = FTW_REFERENCE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        form = TestView(self.portal, self.portal.REQUEST)
        form.update()
        self.widget = form.form_instance.widgets['relation']
        tns = self.portal.portal_properties.site_properties.types_not_searched
        tns = tns + ('Folder',)
        self.portal.portal_properties.site_properties.types_not_searched = tns

    def test_traversable_types_default(self):
        expected = ['Document', 'Event', 'File', 'Folder', 'Image',
                    'Link', 'News Item', 'Topic', 'Collection']
        result = get_traversal_types(self.widget)
        self.assertEquals(8, len(result))
        for item in result:
            self.assertTrue(item in expected)

    def test_traversable_types_more_blocked(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceSettings)
        proxy.block_traversal_additional = ('Document', 'Event')

        result = get_traversal_types(self.widget)
        self.assertEquals(6, len(result))
        self.assertTrue('Document' not in result)
        self.assertTrue('Event' not in result)

    def test_traversable_types_more_allowed(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceSettings)
        proxy.traverse_additional = ('Folder',)

        result = get_traversal_types(self.widget)
        self.assertEquals(9, len(result))
        self.assertIn('Folder', result)

    def test_selectable_types_more_allowed(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceSettings)
        proxy.select_additional = ('Folder',)

        result = get_selectable_types(self.widget)
        self.assertEquals(9, len(result))
        self.assertIn('Folder', result)

    def test_selectable_types_more_blocked(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceSettings)
        proxy.block_additional = ('Document', 'Event')

        result = get_selectable_types(self.widget)
        self.assertEquals(6, len(result))
        self.assertTrue('Document' not in result)
        self.assertTrue('Event' not in result)

    @browsing
    def test_handlebar_templates_available(self, browser):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()
        browser.login().open(view='test-refwidget')
        self.assertTrue(browser.css('#refbrowser-template').first)
        self.assertTrue(browser.css('#node-template').first)
        self.assertTrue(browser.css('#listing-template').first)
