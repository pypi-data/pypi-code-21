from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_traversal_types
from ftw.referencewidget.testing import FTW_REFERENCE_FUNCTIONAL_TESTING
from ftw.referencewidget.tests.views.form import TestView
from unittest2 import TestCase


class TestWidgetConfig(TestCase):
    layer = FTW_REFERENCE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        form = TestView(self.portal, self.portal.REQUEST)
        form.update()
        self.widget = form.form_instance.widgets['relation']
        tns = self.portal.portal_properties.site_properties.types_not_searched
        tns = tns + ('Folder',)
        self.portal.portal_properties.site_properties.types_not_searched = tns

    def test_traversable_types_more_blocked(self):
        self.widget.block_traversal = ['Document', 'Event']

        result = get_traversal_types(self.widget)
        self.assertEquals(6, len(result))
        self.assertTrue('Document' not in result)
        self.assertTrue('Event' not in result)

    def test_traversable_types_more_allowed(self):
        self.widget.allow_traversal = ['Folder']

        result = get_traversal_types(self.widget)
        self.assertEquals(9, len(result))
        self.assertIn('Folder', result)

    def test_selectable_types_more_allowed(self):
        self.widget.selectable = ['Folder']

        result = get_selectable_types(self.widget)
        self.assertEquals(9, len(result))
        self.assertIn('Folder', result)

    def test_selectable_types_more_blocked(self):
        self.widget.nonselectable = ['Document', 'Event']

        result = get_selectable_types(self.widget)
        self.assertEquals(6, len(result))
        self.assertTrue('Document' not in result)
        self.assertTrue('Event' not in result)
