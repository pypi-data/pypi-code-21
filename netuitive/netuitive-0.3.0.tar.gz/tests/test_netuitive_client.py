#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitive` module.
"""

import unittest
import mock

import os
import time
from datetime import datetime

import netuitive

try:
    from cStringIO import StringIO

except ImportError:
    try:
        from StringIO import StringIO

    except ImportError:
        from io import StringIO

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

def getFixtureDirPath():
    path = os.path.join(
        os.path.dirname('tests/'),
        'fixtures')
    return path


def getFixturePath(fixture_name):
    path = os.path.join(getFixtureDirPath(),
                        fixture_name)
    if not os.access(path, os.R_OK):
        print('Missing Fixture ' + path)
    return path


def getFixture(fixture_name):
    with open(getFixturePath(fixture_name), 'r') as f:
        return StringIO(f.read())


class MockResponse(object):

    def __init__(self,
                 resp_data='',
                 headers={'content-type': 'text/plain; charset=utf-8'},
                 code=200,
                 msg='OK',
                 resp_headers=None):

        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = headers
        self.resp_headers = resp_headers

    def read(self):
        return self.resp_data

    def info(self):
        return dict(self.resp_headers)

    def getcode(self):
        return self.code

    def close(self):
        return True


class TestClientSamplePost(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_success(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)

        self.assertTrue(resp)

        self.assertEqual(mock_logging.exception.call_args_list, [])

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general_http(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 500, '', {}, None)
        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)

        self.assertNotEqual(resp, True)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_repeat_failure_general_http(self, mock_logging, mock_post):

        a = netuitive.Client(api_key='apikey')

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        errs = [403, 429, 503, 404, 503, 204, 307, 302, 405, 413]

        for i in range(a.max_post_errors):
            mock_post.return_value = MockResponse(code=errs[i])
            mock_post.side_effect = urllib2.HTTPError(
                a.url, errs[i], '', {}, None)

            resp = a.post(e)

        resp = a.post(e)
        self.assertNotEqual(resp, True)
        self.assertFalse(resp)

        self.assertFalse(a.disabled)

        self.assertEqual(len(e.samples), 0)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.URLError('something')
        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)

        self.assertNotEqual(resp, True)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_null_element_id(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Element()

        resp = a.post(e)

        self.assertEqual(None, resp)
        self.assertEqual(str(mock_logging.exception.call_args_list[0][0][2]),
                         'element id is not set')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_410(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=410)

        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 410, '', {}, None)

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)
        resp2 = a.post(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)

        self.assertTrue(a.disabled)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_418(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=418)
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 418, '', {}, None)
        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)
        resp2 = a.post(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertTrue(a.disabled)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_not_kill_switch_504(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=504)

        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 504, '', {}, None)

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)
        resp2 = a.post(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)

        self.assertFalse(a.disabled)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    def tearDown(self):
        pass


class TestClientEventPost(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_success(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)

        self.assertTrue(resp)

        self.assertEqual(mock_logging.exception.call_args_list, [])

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general_http(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 500, '', {}, None)

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general(self, mock_logging, mock_post):
        mock_post.side_effect = urllib2.URLError('something')

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_410(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=410)
        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 410, '', {}, None)

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)
        resp2 = a.post_event(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertTrue(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_418(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=418)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 418, '', {}, None)

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)
        resp2 = a.post_event(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertTrue(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_not_kill_switch_504(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=504)
        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 504, '', {}, None)

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)
        resp2 = a.post_event(e)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertFalse(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    def tearDown(self):
        pass

class TestClientCheckPost(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_success(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        c = netuitive.Check('check', 'test', 60)

        resp = a.post_check(c)

        self.assertTrue(resp)

        self.assertEqual(mock_logging.exception.call_args_list, [])

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general_http(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 500, '', {}, None)

        e = netuitive.Check('check', 'test', 60)

        resp = a.post_event(e)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general(self, mock_logging, mock_post):
        mock_post.side_effect = urllib2.URLError('something')

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        c = netuitive.Check('check', 'test', 60)

        resp = a.post_check(c)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][0], 'error posting payload to api ingest endpoint (%s): %s')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_410(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=410)
        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 410, '', {}, None)

        c = netuitive.Check('check', 'test', 60)

        resp = a.post_check(c)
        resp2 = a.post_check(c)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertTrue(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_kill_switch_418(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=418)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 418, '', {}, None)

        c = netuitive.Check('check', 'test', 60)

        resp = a.post_check(c)
        resp2 = a.post_check(c)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertTrue(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][0], 'Posting has been disabled.See previous errors for details.')

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_not_kill_switch_504(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=504)
        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        mock_post.side_effect = urllib2.HTTPError(a.url, 504, '', {}, None)

        c = netuitive.Check('check', 'test', 60)

        resp = a.post_check(c)
        resp2 = a.post_check(c)

        self.assertNotEqual(resp, True)
        self.assertFalse(resp2)
        self.assertFalse(a.disabled)
        self.assertEqual(mock_logging.exception.call_args_list[0][0][0], 'error posting payload to api ingest endpoint (%s): %s')

    def tearDown(self):
        pass

class TestClientTimeOffset(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.urllib2.Request')
    @mock.patch('netuitive.client.logging')
    @mock.patch('netuitive.client.time.time')
    @mock.patch('netuitive.client.time.gmtime')
    def test_insync(self, mock_gmtime, mock_time, mock_logging, mock_req, mock_post):

        resp_headers = {
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS, DELETE',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': 3600,
            'Content-Language': 'en-US',
            'Content-Type': 'text/html;charset=UTF-8',
            'Date': 'Thu, 1 Jan 1970 00:00:00 GMT',
            'Server': 'nginx',
            'Vary': 'Accept-Encoding',
            'Vary': 'Origin',
            'X-Application-Context': 'application:8080',
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Length': 2499,
            'Connection': 'Close'
        }

        mock_time.return_value = time.mktime(
            datetime(1970, 1, 1).timetuple())

        mock_gmtime.return_value = datetime(1970, 1, 1).timetuple()

        mock_post.return_value = MockResponse(code=302,
                                              resp_headers=resp_headers)

        a = netuitive.Client(api_key='apikey')

        resp = a.check_time_offset()

        self.assertTrue(0 <= resp <= 1000)
        self.assertTrue(a.time_insync())

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.urllib2.Request')
    @mock.patch('netuitive.client.logging')
    @mock.patch('netuitive.client.time.time')
    @mock.patch('netuitive.client.time.gmtime')
    def test_outsync(self, mock_gmtime, mock_time, mock_logging, mock_req, mock_post):

        resp_headers = {
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS, DELETE',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': 3600,
            'Content-Language': 'en-US',
            'Content-Type': 'text/html;charset=UTF-8',
            'Date': 'Thu, 1 Jan 1970 00:00:00 GMT',
            'Server': 'nginx',
            'Vary': 'Accept-Encoding',
            'Vary': 'Origin',
            'X-Application-Context': 'application:8080',
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Length': 2499,
            'Connection': 'Close'
        }

        mock_time.return_value = time.mktime(
            datetime(1970, 1, 1).timetuple())

        mock_gmtime.return_value = datetime(1971, 1, 1).timetuple()

        mock_post.return_value = MockResponse(code=302,
                                              resp_headers=resp_headers)

        a = netuitive.Client(api_key='apikey')

        resp = a.check_time_offset()

        self.assertEqual(31536000, resp)
        self.assertFalse(a.time_insync())

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.urllib2.Request')
    @mock.patch('netuitive.client.logging')
    @mock.patch('netuitive.client.time.time')
    @mock.patch('netuitive.client.time.gmtime')
    def test_check_time_offset(self, mock_gmtime, mock_time, mock_logging, mock_req, mock_post):

        resp_headers = {
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS, DELETE',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': 3600,
            'Content-Language': 'en-US',
            'Content-Type': 'text/html;charset=UTF-8',
            'Date': 'Thu, 1 Jan 1970 00:00:00 GMT',
            'Server': 'nginx',
            'Vary': 'Accept-Encoding',
            'Vary': 'Origin',
            'X-Application-Context': 'application:8080',
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Length': 2499,
            'Connection': 'Close'
        }

        mock_time.return_value = time.mktime(
            datetime(1970, 1, 1).timetuple())

        mock_gmtime.return_value = datetime(1971, 1, 1).timetuple()

        mock_post.return_value = MockResponse(code=302,
                                              resp_headers=resp_headers)

        a = netuitive.Client(api_key='apikey')

        resp = a.check_time_offset(1456768643)

        rtime = int(time.mktime(
            time.strptime(resp_headers['Date'], "%a, %d %b %Y %H:%M:%S %Z")))

        self.assertEqual(1456768643 - rtime, resp)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
