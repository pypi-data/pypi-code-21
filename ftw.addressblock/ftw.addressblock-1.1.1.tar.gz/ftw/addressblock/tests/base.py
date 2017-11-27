import transaction
from ftw.addressblock.testing import FTW_FUNCTIONAL
from plone.app.testing import setRoles, TEST_USER_ID
from unittest2 import TestCase


class FunctionalTestCase(TestCase):
    layer = FTW_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
