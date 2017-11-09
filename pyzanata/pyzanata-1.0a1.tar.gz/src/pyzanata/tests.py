# -*- coding: utf-8 -*-
import responses
import unittest


class TestZanataClient(unittest.TestCase):

    def test_structure(self):
        from pyzanata import ZanataCredentials
        from pyzanata import ZanataClient
        from pyzanata import ZanataResource
        from pyzanata import ZanataEndpoint
        from pyzanata import ZanataMethod
        credentials = ZanataCredentials(
            'https://foo.bar/api',
            'user',
            'secret'
        )
        zc = ZanataClient(credentials)
        zr = zc.AccountResource
        self.assertTrue(isinstance(zr, ZanataResource))
        ze = zr.accounts
        self.assertTrue(isinstance(ze, ZanataEndpoint))
        zm = ze.PUT
        self.assertTrue(isinstance(zm, ZanataMethod))
        self.assertTrue(callable(zm))

    def test_method(self):
        from pyzanata import ZanataCredentials
        from pyzanata import ZanataClient
        credentials = ZanataCredentials(
            'https://foo.bar/api',
            'foobarbaz',
            'secret'
        )
        zc = ZanataClient(credentials)
        zm = zc.AccountResource.accounts.GET
        self.assertEqual(
            zm._path(username='foobarbaz'),
            '/accounts/u/foobarbaz'
        )
        self.assertEqual(
            zm._url(username='foobarbaz'),
            'https://foo.bar/api/accounts/u/foobarbaz'
        )
        self.assertEqual(
            zm._headers,
            {'Accept': 'application/vnd.zanata.account+json'}
        )

    @responses.activate
    def test_method_call(self):
        expected_resp_json = [{
            u'defaultType': u'Podir',
            u'id': u'my-test',
            u'links': [{
                u'href': u'p/my-test',
                u'rel': u'self',
                u'type': u'application/vnd.zanata.project+json'
            }],
            u'name': u'MyWebsites Test',
            u'status': u'ACTIVE',
        }]
        responses.add(
            responses.GET,
            'https://foo.bar/api/projects',
            json=expected_resp_json,
            status=200
        )
        from pyzanata import ZanataCredentials
        from pyzanata import ZanataClient
        credentials = ZanataCredentials(
            'https://foo.bar/api',
            'foobarbaz',
            'secret'
        )
        zc = ZanataClient(credentials)
        resp = zc.ProjectsResource.projects.GET()
        got_resp = resp.json()
        self.assertDictEqual(got_resp[0], expected_resp_json[0])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZanataClient))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite())
