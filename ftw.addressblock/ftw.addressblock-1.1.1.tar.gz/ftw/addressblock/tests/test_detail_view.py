from ftw.addressblock.tests.base import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from plone.app.textfield import RichTextValue


class DetailViewTests(FunctionalTestCase):

    def setUp(self):
        super(DetailViewTests, self).setUp()
        self.grant('Manager')

    @browsing
    def test_detail_view_renders_fallback_document_heading(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertEquals(
            u'Contact',
            browser.css('h1.documentFirstHeading').first.text
        )

    @browsing
    def test_detail_view_renders_custom_document_heading(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .titled(u'The Title Of The Addressblock')
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertEquals(
            u'The Title Of The Addressblock',
            browser.css('h1.documentFirstHeading').first.text
        )

    @browsing
    def test_detail_view_does_not_render_email(self, browser):
        """
        The email must not be rendered if the block is told not to do so.
        """
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .having(address_title=u'Apple Store')
                              .having(email=u'no@domain.tld')
                              .having(show_email=False)
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertEquals(
            ['Apple Store'],
            browser.css('.addressText').text
        )

    @browsing
    def test_detail_view_extended_example(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .having(address_title=u'Apple Store')
                              .having(department=u'Sales')
                              .having(address=u'1 Infinite Loop')
                              .having(zip_code=u'95014')
                              .having(city=u'Cupertino')
                              .having(country=u'USA')  # Will not be rendered.
                              .having(show_email=True)
                              .having(email=u'no@domain.tld')
                              .having(phone=u'+1 408-606-5775')
                              .having(fax=u'+1 408-606-5776')
                              .having(www=u'https://www.apple.com')
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertEquals(
            [
                'Apple Store\n'
                'Sales\n'
                '1 Infinite Loop\n'
                '95014 Cupertino\n'
                'Phone +1 408-606-5775\n'
                'Fax +1 408-606-5776\n'
                'no@domain.tld\n'
                'https://www.apple.com',
            ],
            browser.css('.addressText').text
        )

    @browsing
    def test_detail_view_renders_opening_hours(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .having(address_title=u'Apple Store')
                              .having(opening_hours=RichTextValue(u'<p>My Opening Hours<p>'))
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertIn(
            u'My Opening Hours',
            browser.css('#content-core').first.text
        )

    @browsing
    def test_detail_view_renders_accessibility_information(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .having(address_title=u'Apple Store')
                              .having(accessibility=RichTextValue(u'<p>Reserved Parking<p>'))
                              .within(page))
        browser.login().visit(addressblock, view='addressblock_detail_view')
        self.assertIn(
            u'Reserved Parking',
            browser.css('#content-core').first.text
        )
