from ftw.addressblock.tests.base import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing.mailing import Mailing
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


FORM_DATA = {
    'Name': u'Zaph\xf6d Beeblebrox',
    'Email': u'z.beeblebrox@endofworld.com',
    'Subject': u'Don\'t p\xe4nic',
    'Message': '42',
}


class ContactTests(FunctionalTestCase):

    def setUp(self):
        super(ContactTests, self).setUp()
        self.grant('Manager')

        Mailing(self.portal).set_up()

        self.portal.manage_changeProperties({
            'email_from_name': u'Pl\xf6ne Admin',
            'email_from_address': u'plone@admin.ch',
        })

        transaction.commit()

    @browsing
    def test_cancel_form(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))
        browser.login().open(addressblock, view='contact')
        browser.find('Cancel').click()
        self.assertEqual(browser.url, page.absolute_url())

    @browsing
    def test_required_fields(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))
        browser.login().open(addressblock, view='contact')
        browser.find('Send Email').click()

        self.assertIn('kssattr-fieldname-form.widgets.sender error',
                      browser.contents)
        self.assertIn('kssattr-fieldname-form.widgets.email error',
                      browser.contents)
        self.assertIn('kssattr-fieldname-form.widgets.subject error',
                      browser.contents)
        self.assertIn('kssattr-fieldname-form.widgets.message error',
                      browser.contents)

    @browsing
    def test_send_form(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))

        browser.login().open(addressblock, view='contact')

        browser.fill(FORM_DATA)

        browser.find('Send Email').click()

        self.assertEqual(browser.url,
                         page.absolute_url())

        self.assertEquals(['The email was sent.'],
                          statusmessages.info_messages())

        self.assertTrue(Mailing(self.portal).has_messages())
        mailcontent = Mailing(self.portal).pop()

        self.assertIn(
            '\nSubject: =?utf-8?q?Don=27t_p=C3=A4nic?=\n',
            mailcontent
        )
        self.assertIn(
            FORM_DATA['Message'],
            mailcontent
        )
        self.assertIn(
            u'\nReply-To: =?utf-8?q?Zaph=C3=B6d_Beeblebrox_=3Cz=2Ebeeblebrox=40endofworld=2Ecom=3E?=\n',
            mailcontent
        )
        self.assertIn(
            u'\nFrom: =?utf-8?q?Pl=C3=B6ne_Admin_=3Cplone=40admin=2Ech=3E?=\n',
            mailcontent
        )

    @browsing
    def test_encode_replyto_always(self, browser):
        """
        Test that makes sure that the Reply-To header is always encoded.
        """
        page = create(Builder('sl content page')
                      .titled(u'page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))

        browser.login().open(addressblock, view='contact')
        browser.fill(FORM_DATA)

        browser.fill({'Name': 'Hans: Peter'})

        browser.find('Send Email').click()

        self.assertEqual(browser.url, page.absolute_url())

        mailcontent = Mailing(self.portal).pop()

        self.assertIn(
            '\nReply-To: Hans: Peter <z.beeblebrox@endofworld.com>\n',
            mailcontent)

    @browsing
    def test_comma_in_sender_name_will_be_replaced(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))

        browser.login().open(addressblock, view='contact')
        browser.fill(FORM_DATA)

        browser.fill({'Name': 'Zaph\xc3\xb6d,Beeblebrox'})

        browser.find('Send Email').click()

        self.assertEqual(browser.url, page.absolute_url())

        mailcontent = Mailing(self.portal).pop()

        self.assertIn(
            '\nReply-To: =?utf-8?q?Zaph=C3=B6d_Beeblebrox_=3Cz=2Ebeeblebrox=40endofworld=2Ecom=3E?=\n',
            mailcontent)

    def tearDown(self):
        super(ContactTests, self).tearDown()
        Mailing(self.layer['portal']).tear_down()


class TestGetToAddress(FunctionalTestCase):

    def setUp(self):
        super(TestGetToAddress, self).setUp()
        self.grant('Manager')
        Mailing(self.portal).set_up()

    @browsing
    def test_get_addressblock_email(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page)
                              .having(email='test@test.ch'))
        browser.login().open(addressblock, view='contact')

        browser.fill(FORM_DATA)
        browser.find('Send Email').click()

        mailcontent = Mailing(self.portal).pop()

        self.assertIn('To: test@test.ch',
                      mailcontent)

    @browsing
    def test_get_subsite_email(self, browser):
        page = create(Builder('sl content page'))
        subsite = create(Builder('subsite')
                         .within(page)
                         .having(from_email='test@test.ch'))
        browser.login().open(subsite, view='contact')

        browser.fill(FORM_DATA)
        browser.find('Send Email').click()

        mailcontent = Mailing(self.portal).pop()

        self.assertIn('To: test@test.ch',
                      mailcontent)

    @browsing
    def test_get_fallback_email(self, browser):
        page = create(Builder('sl content page'))
        browser.login().open(page, view='contact')

        browser.fill(FORM_DATA)
        browser.find('Send Email').click()

        mailcontent = Mailing(self.portal).pop()

        self.assertIn('To: test@localhost',
                      mailcontent)

    def tearDown(self):
        super(TestGetToAddress, self).tearDown()
        Mailing(self.layer['portal']).tear_down()


class TestFeedbackWithCaptcha(FunctionalTestCase):

    def setUp(self):
        super(TestFeedbackWithCaptcha, self).setUp()
        self.grant('Manager')

    @browsing
    def test_captcha_is_hidden_if_not_configured(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page))

        browser.logout().visit(addressblock, view='contact')

        # ReCaptcha is in the label which is only
        # rendered if the field is visible
        self.assertFalse(browser.css('#formfield-form-widgets-captcha label'),
                         'The captcha should be hidden.')

    @browsing
    def test_captcha_is_used_if_configured(self, browser):
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page))

        registry = getUtility(IRegistry)
        registry['plone.formwidget.recaptcha.interfaces.'
                 'IReCaptchaSettings.private_key'] = u'PRIVATE_KEY'
        registry['plone.formwidget.recaptcha.interfaces.'
                 'IReCaptchaSettings.public_key'] = u'PUBLIC_KEY'
        transaction.commit()

        browser.logout().visit(addressblock, view='contact')

        self.assertTrue(browser.css('#formfield-form-widgets-captcha label'),
                        'The captcha should be visible.')

    @browsing
    def test_captcha_no_component_lookup_error(self, browser):
        """
        A `ComponentLookupError` was thrown if you first opened the feedback
        form in your browser as an unauthorized user and then opened the
        same feedback form as an authorized user (where the captcha field
        should not be displayed).
        This test makes sure that this does not happen any more. Please see
        `ftw.addressblock.contact.browser.contact.ContactForm#updateWidgets`.
        """
        page = create(Builder('sl content page'))
        addressblock = create(Builder('sl addressblock')
                              .within(page))

        registry = getUtility(IRegistry)
        registry['plone.formwidget.recaptcha.interfaces.IReCaptchaSettings.private_key'] = u'PRIVATE_KEY'
        registry['plone.formwidget.recaptcha.interfaces.IReCaptchaSettings.public_key'] = u'PUBLIC_KEY'
        transaction.commit()

        browser.logout().visit(addressblock, view='contact')
        browser.login().visit(addressblock, view='contact')

        # Our test passes if the page is loading and contains the feedback
        # form.
        self.assertEqual(len(browser.css('#form')), 1)
