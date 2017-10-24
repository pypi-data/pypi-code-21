from datetime import datetime
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import override_settings
from mock import patch
from ucamwebauth.tests import create_wls_response


def assert_contains_in_order(actual, expected):
    """
    assert that all the strings in *expected* occur in the *actual* in the order in which they are listed

    :param actual: target string to search
    :param expected: collection of strings to search for
    """
    for query in expected:
        query = str(query)
        index = actual.find(query)
        if index == -1:
            raise AssertionError("'%s' not found in target" % query)
        else:
            actual = actual[index + len(query):]


user_dict = {
    'test0001': 'Testy Mike',
    'it123': 'Ivanna Tinkle',
    'ac123': 'Al Coholic',
    'hr123': 'Harry Rump',
    'bl123': 'Bill Loney',
    'jk123': 'Joe King'
}


PASSWORD = 'notsecret'


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, CELERY_ALWAYS_EAGER=True, BROKER_BACKEND='memory',
                   DEBUG=True)
class UnitTestCase(TestCase):

    def setUp(self):

        def return_visible_name_by_crsid_side_effect(*args):
            return user_dict[args[0]]

        return_visible_name_by_crsid = self.patch("ucamlookup.signals.return_visibleName_by_crsid")
        return_visible_name_by_crsid.side_effect = return_visible_name_by_crsid_side_effect

    def do_test_login(self, username, superuser=False):
        """
        Do a fake login.

        :param username: username
        :param superuser: whether or not a super user
        :return: logged in user
        """
        if username in user_dict:
            user = User.objects.create_superuser(username, "%s@cam.ac.uk" % username, PASSWORD) \
                if superuser else User.objects.create_user(username, password=PASSWORD)
            self.client.login(username=username, password=PASSWORD)
            return user

    def do_admin_login(self, username):
        """
        Do a fake adminlogin.

        :param username: username
        :return: logged in admin user
        """
        user = self.do_test_login(username)
        user.is_superuser = True
        user.save()
        return user

    def get_html_test_target(self, response):
        """
        Returns the test_target div for a valid html response encapsulated with BeautifulSoup.

        :param response: http response
        :return: a BeautifulSoup instance

        """
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], "text/html; charset=utf-8")
        return BeautifulSoup(response.content, 'html.parser').find("div", {"class": "test_target"})

    def assert_element_with_text(self, target, element, text):
        """
        assert that an HTML element with text can be found in target

        :param target: bs4 html tree
        :param element: element to find
        :param text: text in element to match
        """
        for el in target.find_all(element):
            if el.get_text().strip() == text:
                return
        self.fail("Couldn't find element '%s' with text '%s'" % (element, text))

    def patch(self, target_name, side_effect=None):
        """
        Patching helper method

        :param target_name: name of target method to patch
        :param side_effect: optional side_effect to set
        :return: the patched target method
        """
        patcher = patch(target_name)
        target = patcher.start()
        self.addCleanup(patcher.stop)
        if side_effect:
            target.side_effect = side_effect
        return target


def do_test_login(self, user="user1"):
    with self.settings(UCAMWEBAUTH_CERTS={901: """-----BEGIN CERTIFICATE-----
MIIDzTCCAzagAwIBAgIBADANBgkqhkiG9w0BAQQFADCBpjELMAkGA1UEBhMCR0Ix
EDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEgMB4GA1UEChMX
VW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1dGluZyBTZXJ2
aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4gREVNTyBwdWJs
aWMga2V5IDEwHhcNMDUwNzI2MTMyMTIwWhcNMDUwODI1MTMyMTIwWjCBpjELMAkG
A1UEBhMCR0IxEDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEg
MB4GA1UEChMXVW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1
dGluZyBTZXJ2aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4g
REVNTyBwdWJsaWMga2V5IDEwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBALhF
i9tIZvjYQQRfOzP3cy5ujR91ZntQnQehldByHlchHRmXwA1ot/e1WlHPgIjYkFRW
lSNcSDM5r7BkFu69zM66IHcF80NIopBp+3FYqi5uglEDlpzFrd+vYllzw7lBzUnp
CrwTxyO5JBaWnFMZrQkSdspXv89VQUO4V4QjXV7/AgMBAAGjggEHMIIBAzAdBgNV
HQ4EFgQUgjC6WtA4jFf54kxlidhFi8w+0HkwgdMGA1UdIwSByzCByIAUgjC6WtA4
jFf54kxlidhFi8w+0HmhgaykgakwgaYxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdF
bmdsYW5kMRIwEAYDVQQHEwlDYW1icmlkZ2UxIDAeBgNVBAoTF1VuaXZlcnNpdHkg
b2YgQ2FtYnJpZGdlMS0wKwYDVQQLEyRDb21wdXRpbmcgU2VydmljZSBERU1PIFJh
dmVuIFNlcnZpY2UxIDAeBgNVBAMTF1JhdmVuIERFTU8gcHVibGljIGtleSAxggEA
MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEEBQADgYEAsdyB+9szctHHIHE+S2Kg
LSxbGuFG9yfPFIqaSntlYMxKKB5ba/tIAMzyAOHxdEM5hi1DXRsOok3ElWjOw9oN
6Psvk/hLUN+YfC1saaUs3oh+OTfD7I4gRTbXPgsd6JgJQ0TQtuGygJdaht9cRBHW
wOq24EIbX5LquL9w+uvnfXw=
-----END CERTIFICATE-----"""}):
        self.client.get(reverse('raven_return'),
                        {'WLS-Response': create_wls_response(raven_issue=datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
                                                             raven_url=settings.UCAMWEBAUTH_RETURN_URL,
                                                             raven_principal=user)})
        self.assertIn('_auth_user_id', self.client.session)
