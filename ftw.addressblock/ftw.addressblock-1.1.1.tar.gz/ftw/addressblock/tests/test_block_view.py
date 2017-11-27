from ftw.addressblock.tests.base import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from plone.app.textfield import RichTextValue
from zope.component import getMultiAdapter


class BlockViewTests(FunctionalTestCase):

    def setUp(self):
        super(BlockViewTests, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_renders_default_title(self, browser):
        """
        This test makes sure that the the block renders a fallback
        title if no title is provided.
        """
        page = create(Builder('sl content page'))
        create(Builder('sl addressblock')
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            u'Contact',
            browser.css('.sl-block h2').first.text
        )

    @browsing
    def test_block_renders_link_to_detail_view(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'My Page'))
        create(Builder('sl addressblock')
               .titled(u'My Block')
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            ['Address / Map'],
            browser.css('.sl-block li').text
        )
        self.assertEqual(
            'http://nohost/plone/my-page/my-block/addressblock_detail_view',
            browser.css('.sl-block li a').first.attrib['href']
        )

    @browsing
    def test_block_renders_custom_title(self, browser):
        """
        This test makes sure that the the block renders the custom title.
        """
        page = create(Builder('sl content page'))
        create(Builder('sl addressblock')
               .titled(u'The Title Of The Addressblock')
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            u'The Title Of The Addressblock',
            browser.css('.sl-block h2').first.text
        )

    def test_has_team(self):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page))
        view = getMultiAdapter(
            (addressblock, self.request),
            name='block_view'
        )
        self.assertFalse(view.has_team())
        create(Builder('sl content page')
               .titled(u'Team')
               .having(id='team')
               .within(page))
        self.assertTrue(view.has_team())

    @browsing
    def test_block_renders_link_to_opening_hours(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'My Page'))
        create(Builder('sl addressblock')
               .titled(u'My Block')
               .having(opening_hours=RichTextValue(u'My Opening Hours'))
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            [
                'Address / Map',
                'Opening Hours',
            ],
            browser.css('.sl-block li').text
        )
        self.assertEqual(
            'http://nohost/plone/my-page/my-block/addressblock_detail_view#opening_hours',
            browser.css('.sl-block li a')[1].attrib['href']
        )

    @browsing
    def test_block_renders_link_to_accessibility(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'My Page'))
        create(Builder('sl addressblock')
               .titled(u'My Block')
               .having(accessibility=RichTextValue(u'Reserved parking'))
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            [
                'Address / Map',
                'Buildings Accessibility',
            ],
            browser.css('.sl-block li').text
        )
        self.assertEqual(
            'http://nohost/plone/my-page/my-block/addressblock_detail_view#accessibility',
            browser.css('.sl-block li a')[1].attrib['href']
        )

    @browsing
    def test_block_renders_link_to_team(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'My Page'))
        create(Builder('sl content page')
               .titled(u'Team')
               .having(id='team')
               .within(page))
        create(Builder('sl addressblock')
               .titled(u'My Block')
               .within(page))
        browser.login().visit(page)
        self.assertEquals(
            [
                'Address / Map',
                'Team',
            ],
            browser.css('.sl-block li').text
        )
        self.assertEqual(
            './team',
            browser.css('.sl-block li a')[1].attrib['href']
        )

    @browsing
    def test_block_extended_example(self, browser):
        """
        The address block only renders very few of the fields, e.g. the address
        title and the phone number. The other data must be accessed through the
        detail view of the block.
        """
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .having(address_title=u'Apple Store')
                              .having(department=u'Sales')  # Will not be rendered.
                              .having(address=u'1 Infinite Loop')  # Will not be rendered.
                              .having(zip_code=u'95014')  # Will not be rendered.
                              .having(city=u'Cupertino')  # Will not be rendered.
                              .having(country=u'USA')  # Will not be rendered.
                              .having(show_email=True)   # Will not be rendered.
                              .having(email=u'no@domain.tld')   # Will not be rendered.
                              .having(phone=u'+1 408-606-5775')
                              .having(www=u'https://www.apple.com')   # Will not be rendered.
                              .within(page))
        browser.login().visit(page)
        self.assertEquals(
            [
                'Contact '
                'Apple Store '
                'Phone +1 408-606-5775\n\n'
                'Address / Map '
                'Contact Form'
            ],
            browser.css('#content-core').text
        )
