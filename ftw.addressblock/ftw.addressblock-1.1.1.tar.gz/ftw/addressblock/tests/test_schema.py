from ftw.addressblock.content.addressblock import IAddressBlockSchema
from ftw.addressblock.interfaces import IAddressBlock
from ftw.addressblock.tests.base import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility


class AddressblockSchemaTests(FunctionalTestCase):

    def setUp(self):
        super(AddressblockSchemaTests, self).setUp()
        self.grant('Manager')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='ftw.addressblock.AddressBlock')
        schema = fti.lookupSchema()
        self.assertEqual(IAddressBlockSchema, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='ftw.addressblock.AddressBlock')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='ftw.addressblock.AddressBlock')
        factory = fti.factory
        addressblock = createObject(factory)
        self.assertTrue(IAddressBlock.providedBy(addressblock))

    @browsing
    def test_default_value_of_addresstitle_is_title_of_parent(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'Will Be The Default Value When Creating The Block'))
        browser.login().visit(page, view='++add++ftw.addressblock.AddressBlock')
        self.assertEqual(
            u'Will Be The Default Value When Creating The Block',
            browser.find_field_by_text('Address title').value
        )

    @browsing
    def test_country_has_default_value(self, browser):
        page = create(Builder('sl content page'))
        browser.login().visit(page, view='++add++ftw.addressblock.AddressBlock')
        self.assertEqual(
            u'Switzerland',
            browser.find_field_by_text('Country').value
        )
