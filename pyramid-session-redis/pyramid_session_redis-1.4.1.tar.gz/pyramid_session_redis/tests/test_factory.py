# -*- coding: utf-8 -*-

import itertools
import unittest
import pprint

from pyramid import testing
from ..compat import cPickle
from ..util import encode_session_payload, int_time, LAZYCREATE_SESSION
from ..exceptions import (InvalidSession,
                          InvalidSession_NoSessionCookie,
                          InvalidSession_NotInBackend,
                          InvalidSession_DeserializationError,
                          InvalidSession_PayloadTimeout,
                          InvalidSession_PayloadLegacy,
                          RawDeserializationError,
                          )

from .. import RedisSessionFactory
from .test_config import dummy_id_generator
import webob


class _TestRedisSessionFactoryCore(unittest.TestCase):

    def _makeOne(self, request, secret='secret', **kw):
        from .. import RedisSessionFactory
        session = RedisSessionFactory(secret, **kw)(request)
        return session

    def _makeOneSession(self, redis, session_id, **kw):
        from ..session import RedisSession
        session = RedisSession(
            redis=redis,
            session_id=session_id,
            **kw
        )
        return session

    def _register_callback(self, request, session):
        import functools
        from .. import _finished_callback
        finished_callback = functools.partial(
            _finished_callback,
            session
        )
        request.add_finished_callback(finished_callback)

    def _assert_is_a_header_to_set_cookie(self, header_value):
        # The negative assertion below is the least complicated option for
        # asserting that a Set-Cookie header sets a cookie rather than deletes
        # a cookie. This helper method is to help make that intention clearer
        # in the tests.
        self.assertNotIn('Max-Age=0', header_value)

    def _get_session_id(self, request):
        from ..util import create_unique_session_id
        redis = request.registry._redis_sessions
        session_id = create_unique_session_id(redis, timeout=100,
                                              serialize=cPickle.dumps)
        return session_id

    def _serialize(self, session_id, secret='secret'):
        from pyramid.session import signed_serialize
        return signed_serialize(session_id, secret)

    def _set_session_cookie(self, request, session_id, cookie_name='session',
                            secret='secret'):
        cookieval = self._serialize(session_id, secret=secret)
        request.cookies[cookie_name] = cookieval

    def _make_request(self, request_old=None):
        from . import DummyRedis
        if request_old:
            # grab the registry data to persist, otherwise it gets discarded
            # and transfer it to a new request
            _redis_sessions = request_old.registry._redis_sessions
            request = testing.DummyRequest()
            request.registry._redis_sessions = _redis_sessions
        else:
            request = testing.DummyRequest()
            request.registry._redis_sessions = DummyRedis()
        request.exception = None
        return request


class TestRedisSessionFactory(_TestRedisSessionFactoryCore):

    def test_ctor_no_cookie(self):
        """
        # original test
        request = self._make_request()
        session = self._makeOne(request)
        session_dict = session.from_redis()['m']
        self.assertDictEqual(session_dict, {})
        self.assertIs(session.new, True)

        # calling from_redis should not happen in 1.4.x+
        """
        request = self._make_request()
        session = self._makeOne(request)
        session_dict = session.managed_dict
        self.assertDictEqual(session_dict, {})
        self.assertIs(session.new, True)

    def test_ctor_with_cookie_still_valid(self):
        request = self._make_request()
        session_id_in_cookie = self._get_session_id(request)
        self._set_session_cookie(request=request,
                                 session_id=session_id_in_cookie)
        session = self._makeOne(request)
        self.assertEqual(session.session_id, session_id_in_cookie)
        self.assertIs(session.new, False)

    def test_ctor_with_bad_cookie(self):
        request = self._make_request()
        session_id_in_cookie = self._get_session_id(request)
        invalid_secret = 'aaaaaa'
        self._set_session_cookie(request=request,
                                 session_id=session_id_in_cookie,
                                 secret=invalid_secret)
        session = self._makeOne(request)
        self.assertNotEqual(session.session_id, session_id_in_cookie)
        self.assertIs(session.new, True)

    def test_session_id_not_in_redis(self):
        request = self._make_request()
        session_id_in_cookie = self._get_session_id(request)
        self._set_session_cookie(request=request,
                                 session_id=session_id_in_cookie)
        redis = request.registry._redis_sessions
        redis.store = {}  # clears keys in DummyRedis
        session = self._makeOne(request)
        self.assertNotEqual(session.session_id, session_id_in_cookie)
        self.assertIs(session.new, True)

    def test_factory_parameters_used_to_set_cookie(self):
        import re
        import webob
        cookie_name = 'testcookie'
        cookie_max_age = 300
        cookie_path = '/path'
        cookie_domain = 'example.com'
        cookie_secure = True
        cookie_httponly = False
        secret = 'test secret'

        request = self._make_request()
        session = request.session = self._makeOne(
            request,
            cookie_name=cookie_name,
            cookie_max_age=cookie_max_age,
            cookie_path=cookie_path,
            cookie_domain=cookie_domain,
            cookie_secure=cookie_secure,
            cookie_httponly=cookie_httponly,
            secret=secret,
        )
        session['key'] = 'value'
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)

        # Make another response and .set_cookie() using the same values and
        # settings to get the expected header to compare against

        # note - webob 1.7 no longer supports name+value kwargs
        response_to_check_against = webob.Response()
        response_to_check_against.set_cookie(
            cookie_name,
            self._serialize(session_id=request.session.session_id,
                            secret=secret),
            max_age=cookie_max_age,
            path=cookie_path,
            domain=cookie_domain,
            secure=cookie_secure,
            httponly=cookie_httponly,
        )
        expected_header = response_to_check_against.headers.getall(
            'Set-Cookie')[0]
        remove_expires_attribute = lambda s: re.sub('Expires ?=[^;]*;', '', s,
                                                    flags=re.IGNORECASE)
        self.assertEqual(remove_expires_attribute(set_cookie_headers[0]),
                         remove_expires_attribute(expected_header))
        # We have to remove the Expires attributes from each header before the
        # assert comparison, as we cannot rely on their values to be the same
        # (one is generated after the other, and may have a slightly later
        # Expires time). The Expires value does not matter to us as it is
        # calculated from Max-Age.

    def test_factory_parameters_used_to_delete_cookie(self):
        import webob
        cookie_name = 'testcookie'
        cookie_path = '/path'
        cookie_domain = 'example.com'

        request = self._make_request()
        self._set_session_cookie(request=request,
                                 cookie_name=cookie_name,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(
            request,
            cookie_name=cookie_name,
            cookie_path=cookie_path,
            cookie_domain=cookie_domain,
        )
        session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)

        # Make another response and .delete_cookie() using the same values and
        # settings to get the expected header to compare against
        response_to_check_against = webob.Response()
        response_to_check_against.delete_cookie(
            cookie_name,
            path=cookie_path,
            domain=cookie_domain,
        )
        expected_header = response.headers.getall('Set-Cookie')[0]
        self.assertEqual(set_cookie_headers[0], expected_header)

    # The tests below with names beginning with test_new_session_ test cases
    # where first access to request.session creates a new session, as in
    # test_ctor_no_cookie, test_ctor_with_bad_cookie and
    # test_session_id_not_in_redis.

    def test_new_session_cookie_on_exception_true_no_exception(self):
        # cookie_on_exception is True by default, no exception raised
        import webob
        request = self._make_request()
        request.session = self._makeOne(request)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_cookie_on_exception_true_exception(self):
        # cookie_on_exception is True by default, exception raised
        import webob
        request = self._make_request()
        request.session = self._makeOne(request)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_cookie_on_exception_false_no_exception(self):
        # cookie_on_exception is False, no exception raised
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, cookie_on_exception=False)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_cookie_on_exception_false_exception(self):
        # cookie_on_exception is False, exception raised
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, cookie_on_exception=False)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_new_session_invalidate(self):
        # new session -> invalidate()
        import webob
        request = self._make_request()
        request.session = self._makeOne(request)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        request.session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_new_session_session_after_invalidate_coe_True_no_exception(self):
        # new session -> invalidate() -> new session
        # cookie_on_exception is True by default, no exception raised
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request)
        session['a'] = 1  # ensure a lazycreate is triggered
        session.invalidate()
        session['key'] = 'value'
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_session_after_invalidate_coe_True_exception(self):
        # new session -> invalidate() -> new session
        # cookie_on_exception is True by default, exception raised
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request)
        session['a'] = 1  # ensure a lazycreate is triggered
        session.invalidate()
        session['key'] = 'value'
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_session_after_invalidate_coe_False_no_exception(self):
        # new session -> invalidate() -> new session
        # cookie_on_exception is False, no exception raised
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request,
                                                  cookie_on_exception=False)
        session.invalidate()
        session['key'] = 'value'
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_new_session_session_after_invalidate_coe_False_exception(self):
        # new session -> invalidate() -> new session
        # cookie_on_exception is False, exception raised
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request,
                                                  cookie_on_exception=False)
        session.invalidate()
        session['key'] = 'value'
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_new_session_multiple_invalidates(self):
        # new session -> invalidate() -> new session -> invalidate()
        # Invalidate more than once, no new session after last invalidate()
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request)
        session['a'] = 1  # ensure a lazycreate is triggered
        session.invalidate()
        session['key'] = 'value'
        session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_new_session_multiple_invalidates_with_no_new_session_in_between(
        self
    ):
        # new session -> invalidate() -> invalidate()
        # Invalidate more than once, no new session in between invalidate()s,
        # no new session after last invalidate()
        import webob
        request = self._make_request()
        session = request.session = self._makeOne(request)
        session['a'] = 1  # ensure a lazycreate is triggered
        session.invalidate()
        session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_new_session_int_time(self):
        # new request
        request = self._make_request()

        # default behavior: we use int
        session = request.session = self._makeOne(request)
        session['a'] = 1  # ensure a lazycreate is triggered
        self.assertEqual(session.created, int(session.created))

    # The tests below with names beginning with test_existing_session_ test
    # cases where first access to request.session returns an existing session,
    # as in test_ctor_with_cookie_still_valid.

    def test_existing_session(self):
        import webob
        request = self._make_request()
        self._set_session_cookie(
            request=request,
            session_id=self._get_session_id(request),
        )
        request.session = self._makeOne(request)
        response = webob.Response()
        request.response_callbacks[0](request, response)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_existing_session_invalidate(self):
        # existing session -> invalidate()
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        request.session = self._makeOne(request)
        request.session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self.assertIn('Max-Age=0', set_cookie_headers[0])

    def test_existing_session_invalidate_nodupe(self):
        """
        This tests against an edge-case caused when a session is invalidated,
        but no new session interaction takes place. in this situation, the
        callback function introduced by `pyramid_session_redis` can create an
        unwanted placeholder value in redis.

        python -m unittest pyramid_session_redis.tests.test_factory.TestRedisSessionFactory.test_existing_session_invalidate_nodupe
        """
        # existing session -> invalidate()
        import webob
        request = self._make_request()
        session_id = self._get_session_id(request)
        self._set_session_cookie(request=request,
                                 session_id=session_id)
        request.session = self._makeOne(request)
        self._register_callback(request, request.session)
        persisted = request.session.redis.get(session_id)
        self.assertIsNotNone(persisted)

        # invalidate
        request.session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self.assertIn('Max-Age=0', set_cookie_headers[0])

        # manually execute the callbacks
        request._process_finished_callbacks()

        # make sure this isn't in redis
        persisted = request.session.redis.get(session_id)
        self.assertIsNone(persisted)

        # make sure we don't have any keys in redis
        keys = request.session.redis.keys()
        self.assertEqual(len(keys), 0)

    def test_existing_session_session_after_invalidate_coe_True_no_exception(
        self
    ):
        # existing session -> invalidate() -> new session
        # cookie_on_exception is True by default, no exception raised
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request)
        session.invalidate()
        session['key'] = 'value'
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_existing_session_session_after_invalidate_coe_True_exception(
        self
    ):
        # existing session -> invalidate() -> new session
        # cookie_on_exception is True by default, exception raised
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request)
        session.invalidate()
        session['key'] = 'value'
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_existing_session_session_after_invalidate_coe_False_no_exception(
        self
    ):
        # existing session -> invalidate() -> new session
        # cookie_on_exception is False, no exception raised
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request,
                                                  cookie_on_exception=False)
        session.invalidate()
        session['key'] = 'value'
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])

    def test_existing_session_session_after_invalidate_coe_False_exception(
        self
    ):
        # existing session -> invalidate() -> new session
        # cookie_on_exception is False, exception raised
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request,
                                                  cookie_on_exception=False)
        session.invalidate()
        session['key'] = 'value'
        request.exception = Exception()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self.assertIn('Max-Age=0', set_cookie_headers[0])
        # Cancel setting of cookie for new session, but still delete cookie for
        # the earlier invalidate().

    def test_existing_session_multiple_invalidates(self):
        # existing session -> invalidate() -> new session -> invalidate()
        # Invalidate more than once, no new session after last invalidate()
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request)
        session.invalidate()
        session['key'] = 'value'
        session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self.assertIn('Max-Age=0', set_cookie_headers[0])

    def test_existing_session_multiple_invalidates_no_new_session_in_between(
        self
    ):
        # existing session -> invalidate() -> invalidate()
        # Invalidate more than once, no new session in between invalidate()s,
        # no new session after last invalidate()
        import webob
        request = self._make_request()
        self._set_session_cookie(request=request,
                                 session_id=self._get_session_id(request))
        session = request.session = self._makeOne(request)
        session.invalidate()
        session.invalidate()
        response = webob.Response()
        request.response_callbacks[0](request, response)
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)
        self.assertIn('Max-Age=0', set_cookie_headers[0])

    def test_instance_conforms(self):
        from pyramid.interfaces import ISession
        from zope.interface.verify import verifyObject
        request = self._make_request()
        inst = self._makeOne(request)
        verifyObject(ISession, inst)

    def test_adjusted_session_timeout_persists(self):
        request = self._make_request()
        inst = self._makeOne(request)
        inst.adjust_timeout_for_session(555)
        inst.do_persist()
        session_id = inst.session_id
        cookieval = self._serialize(session_id)
        request.cookies['session'] = cookieval
        new_session = self._makeOne(request)
        self.assertEqual(new_session.timeout, 555)

    def test_client_callable(self):
        from . import DummyRedis
        request = self._make_request()
        redis = DummyRedis()
        client_callable = lambda req, **kw: redis
        inst = self._makeOne(request, client_callable=client_callable)
        self.assertEqual(inst.redis, redis)

    def test_session_factory_from_settings(self):
        from .. import session_factory_from_settings
        request = self._make_request()
        settings = {'redis.sessions.secret': 'secret',
                    'redis.sessions.timeout': '999'}
        inst = session_factory_from_settings(settings)(request)
        self.assertEqual(inst.timeout, 999)

    def test_session_factory_from_settings_no_timeout(self):
        from .. import session_factory_from_settings
        """settings should allow `None` and `0`; both becoming `None`"""
        request_none = self._make_request()
        settings_none = {'redis.sessions.secret': 'secret',
                         'redis.sessions.timeout': 'None'}
        inst_none = session_factory_from_settings(settings_none)(request_none)
        self.assertEqual(inst_none.timeout, None)

        request_0 = self._make_request()
        settings_0 = {'redis.sessions.secret': 'secret',
                      'redis.sessions.timeout': '0'}
        inst_0 = session_factory_from_settings(settings_0)(request_0)
        self.assertEqual(inst_0.timeout, None)

    def test_check_response(self):
        from .. import check_response_allow_cookies

        factory = RedisSessionFactory(
            'secret',
            func_check_response_allow_cookies=check_response_allow_cookies,
        )

        # first check we can create a cookie
        request = self._make_request()
        session = factory(request)
        session['a'] = 1  # we only create a cookie on edit
        response = webob.Response()
        request.response_callbacks[0](request, response)
        hdrs_sc = response.headers.getall('Set-Cookie')
        self.assertEqual(len(hdrs_sc), 1)
        self.assertEqual(response.vary, ('Cookie', ))

        # then check we can't set a cookie
        for hdr_exclude in ('expires', 'cache-control'):
            request = self._make_request()
            session = factory(request)
            session['a'] = 1  # we only create a cookie on edit
            response = webob.Response()
            response.headers.add(hdr_exclude, '1')
            request.response_callbacks[0](request, response)
            hdrs_sc = response.headers.getall('Set-Cookie')
            self.assertEqual(len(hdrs_sc), 0)
            self.assertEqual(response.vary, None)

        # just to be safe
        for hdr_dontcare in ('foo', 'bar', ):
            request = self._make_request()
            session = factory(request)
            session['a'] = 1  # we only create a cookie on edit
            response = webob.Response()
            response.headers.add(hdr_dontcare, '1')
            request.response_callbacks[0](request, response)
            hdrs_sc = response.headers.getall('Set-Cookie')
            self.assertEqual(len(hdrs_sc), 1)
            self.assertEqual(response.vary, ('Cookie', ))

    def test_check_response_custom(self):

        def check_response_allow_cookies(response):
            """
            private response
            """
            # The view signals this is cacheable response
            # and we should not stamp a session cookie on it
            cookieless_headers = ["foo", ]
            for header in cookieless_headers:
                if header in response.headers:
                    return False
            return True

        factory = RedisSessionFactory(
            'secret',
            func_check_response_allow_cookies=check_response_allow_cookies,
        )

        # first check we can create a cookie
        request = self._make_request()
        session = factory(request)
        session['a'] = 1  # we only create a cookie on edit
        response = webob.Response()
        request.response_callbacks[0](request, response)
        hdrs_sc = response.headers.getall('Set-Cookie')
        self.assertEqual(len(hdrs_sc), 1)
        self.assertEqual(response.vary, ('Cookie', ))

        # then check we can't set a cookie
        for hdr_exclude in ('foo', ):
            request = self._make_request()
            session = factory(request)
            session['a'] = 1  # we only create a cookie on edit
            response = webob.Response()
            response.headers.add(hdr_exclude, '1')
            request.response_callbacks[0](request, response)
            hdrs_sc = response.headers.getall('Set-Cookie')
            self.assertEqual(len(hdrs_sc), 0)
            self.assertEqual(response.vary, None)

        # just to be safe
        for hdr_dontcare in ('bar', ):
            request = self._make_request()
            session = factory(request)
            session['a'] = 1  # we only create a cookie on edit
            response = webob.Response()
            response.headers.add(hdr_dontcare, '1')
            request.response_callbacks[0](request, response)
            hdrs_sc = response.headers.getall('Set-Cookie')
            self.assertEqual(len(hdrs_sc), 1)
            self.assertEqual(response.vary, ('Cookie', ))


class _TestRedisSessionFactoryCore_UtilsNew(object):

    def _deserialize_session_stored(self, session, deserialize=cPickle.loads):
        """loads session from backend via id, deserializes"""
        _session_id = session.session_id
        _session_data = session.redis.store[_session_id]
        _session_deserialized = deserialize(_session_data)
        return _session_deserialized

    def _set_up_session_in_redis(self, redis, session_id,
                                 session_dict=None, timeout=None,
                                 timeout_trigger=None,
                                 serialize=cPickle.dumps,
                                 python_expires=None,
                                 set_redis_ttl=None,
                                 ):
        if timeout_trigger and not python_expires:  # fix this
            python_expires = True
        if session_dict is None:
            session_dict = {}
        time_now = int_time()
        expires = time_now + timeout if timeout else None
        payload = encode_session_payload(session_dict,
                                         time_now,
                                         timeout,
                                         expires,
                                         timeout_trigger=timeout_trigger,
                                         python_expires=python_expires,
                                         )
        if set_redis_ttl:
            redis.setex(session_id,
                        timeout,
                        serialize(payload),
                        debug='_set_up_session_in_redis'
                        )
        else:
            redis.set(session_id,
                      serialize(payload),
                      debug='_set_up_session_in_redis'
                      )
        return session_id

    def _set_up_session_in_Redis_and_makeOne(self, request, session_id,
                                             session_dict=None, new=True,
                                             timeout=300, timeout_trigger=150,
                                             python_expires=None,
                                             set_redis_ttl=None):
        redis = request.registry._redis_sessions
        self._set_up_session_in_redis(redis=redis, session_id=session_id,
                                      session_dict=session_dict,
                                      timeout=timeout,
                                      timeout_trigger=timeout_trigger,
                                      python_expires=python_expires,
                                      set_redis_ttl=set_redis_ttl,
                                      )
        new_session = lambda: self._set_up_session_in_redis(
            redis=redis,
            session_id=dummy_id_generator(),
            session_dict=session_dict,
            timeout=timeout,
            timeout_trigger=timeout_trigger,
            python_expires=python_expires,
            set_redis_ttl=set_redis_ttl,
        )
        return self._makeOneSession(
            redis,
            session_id,
            new=new,
            new_session=new_session,
            timeout=timeout,
            timeout_trigger=timeout_trigger,
            python_expires=python_expires,
            set_redis_ttl=set_redis_ttl,
        )

    def _prep_new_session(self, session_args):
        import webob
        request = self._make_request()

        request.session = self._makeOne(request, **session_args)
        request.session['a'] = 1  # ensure a lazycreate is triggered
        response = webob.Response()
        request.response_callbacks[0](request, response)  # sets the cookie
        set_cookie_headers = response.headers.getall('Set-Cookie')
        request._process_finished_callbacks()  # runs any persist if needed
        self.assertEqual(len(set_cookie_headers), 1)
        self._assert_is_a_header_to_set_cookie(set_cookie_headers[0])
        # stored_session_data = self._deserialize_session_stored(request.session)
        return request

    def _load_cookie_session_in_new_request(self, request_old, session_id='existing_session', **session_args):
        import webob
        # we need a request, but must persist the redis datastore
        request = self._make_request(request_old=request_old)

        self._set_session_cookie(request=request,
                                 session_id=session_id,
                                 )
        request.session = self._makeOne(request, **session_args)
        response = webob.Response()
        request.response_callbacks[0](request, response)
        request._process_finished_callbacks()  # runs any persist if needed

        self.assertNotIn('Set-Cookie', response.headers)
        # stored_session_data = self._deserialize_session_stored(request.session)
        return request

    def _prep_existing_session(self, session_args):
        import webob
        session_id = 'existing_session'

        def _insert_new_session():
            """
            drop a session into our redis
            this requires a `request` but will only use a DummySession
            """
            request = self._make_request()
            session_existing = self._set_up_session_in_Redis_and_makeOne(
                request,
                session_id,
                session_dict={'visited': True, },
                **session_args
            )
            return request

        # insert the session
        request1 = _insert_new_session()
        request = self._load_cookie_session_in_new_request(request_old=request1, session_id=session_id, **session_args)
        return request

    def _adjust_request_session(self, request, serialize=cPickle.dumps, **kwargs):
        """
        1. deserializes a session's backend datastore, manipulates it, stores it.
        2. generates/returns a new request that loads the modified session

        kwargs = passthtough of session_args
        """
        # grab the active request's session
        _session_id = request.session.session_id
        _session_deserialized = self._deserialize_session_stored(request.session)

        if 'test_adjust_created' in kwargs:
            created = kwargs.pop('test_adjust_created', 0)
            _session_deserialized['c'] += created
        if 'test_adjust_expires' in kwargs:
            expires = kwargs.pop('test_adjust_expires', 0)
            _session_deserialized['x'] += expires

        # reserialize the session and store it in the backend
        _session_serialized = serialize(_session_deserialized)
        request.session.redis.store[_session_id] = _session_serialized
        request.session._resync()


class TestRedisSessionFactory_expiries_v1_4_x(_TestRedisSessionFactoryCore, _TestRedisSessionFactoryCore_UtilsNew):

    # args are used 2x: for NEW and EXISTING session tests

    _args_timeout_trigger_pythonExpires_setRedisTtl = {'timeout': 1200,
                                                       'timeout_trigger': 600,
                                                       'python_expires': True,
                                                       'set_redis_ttl': True,
                                                       }

    _args_timeout_trigger_noPythonExpires_setRedisTtl = {'timeout': 1200,
                                                         'timeout_trigger': 600,
                                                         'python_expires': False,
                                                         'set_redis_ttl': True,
                                                         }

    _args_timeout_noTrigger_pythonExpires_setRedisTtl = {'timeout': 1200,
                                                         'timeout_trigger': None,
                                                         'python_expires': True,
                                                         'set_redis_ttl': True,
                                                         }

    _args_timeout_noTrigger_noPythonExpires_setRedisTtl = {'timeout': 1200,
                                                           'timeout_trigger': None,
                                                           'python_expires': False,
                                                           'set_redis_ttl': True,
                                                           }

    _args_noTimeout_trigger_pythonExpires_setRedisTtl = {'timeout': None,
                                                         'timeout_trigger': 600,
                                                         'python_expires': True,
                                                         'set_redis_ttl': True,
                                                         }

    _args_noTimeout_trigger_noPythonExpires_setRedisTtl = {'timeout': None,
                                                           'timeout_trigger': 600,
                                                           'python_expires': False,
                                                           'set_redis_ttl': True,
                                                           }

    _args_noTimeout_noTrigger_pythonExpires_setRedisTtl = {'timeout': None,
                                                           'timeout_trigger': None,
                                                           'python_expires': True,
                                                           'set_redis_ttl': True,
                                                           }

    _args_noTimeout_noTrigger_noPythonExpires_setRedisTtl = {'timeout': None,
                                                             'timeout_trigger': None,
                                                             'python_expires': False,
                                                             'set_redis_ttl': True,
                                                             }

    _args_timeout_trigger_pythonExpires_noRedisTtl = {'timeout': 1200,
                                                      'timeout_trigger': 600,
                                                      'python_expires': True,
                                                      'set_redis_ttl': False,
                                                      }

    _args_timeout_trigger_noPythonExpires_noRedisTtl = {'timeout': 1200,
                                                        'timeout_trigger': 600,
                                                        'python_expires': False,
                                                        'set_redis_ttl': False,
                                                        }

    _args_timeout_noTrigger_pythonExpires_noRedisTtl = {'timeout': 1200,
                                                        'timeout_trigger': None,
                                                        'python_expires': True,
                                                        'set_redis_ttl': False,
                                                        }

    _args_timeout_noTrigger_noPythonExpires_noRedisTtl = {'timeout': 1200,
                                                          'timeout_trigger': None,
                                                          'python_expires': False,
                                                          'set_redis_ttl': False,
                                                          }

    _args_noTimeout_trigger_pythonExpires_noRedisTtl = {'timeout': None,
                                                        'timeout_trigger': 600,
                                                        'python_expires': True,
                                                        'set_redis_ttl': False,
                                                        }

    _args_noTimeout_trigger_noPythonExpires_noRedisTtl = {'timeout': None,
                                                          'timeout_trigger': 600,
                                                          'python_expires': False,
                                                          'set_redis_ttl': False,
                                                          }

    _args_noTimeout_noTrigger_pythonExpires_noRedisTtl = {'timeout': None,
                                                          'timeout_trigger': None,
                                                          'python_expires': True,
                                                          'set_redis_ttl': False,
                                                          }

    _args_noTimeout_noTrigger_noPythonExpires_noRedisTtl = {'timeout': None,
                                                            'timeout_trigger': None,
                                                            'python_expires': False,
                                                            'set_redis_ttl': False,
                                                            }

    # --------------------------------------------------------------------------
    # new session - timeout
    # --------------------------------------------------------------------------

    def test_scenario_new__timeout_trigger_pythonExpires_setRedisTtl(self):
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[1][2], session_args['timeout'])

    def test_scenario_new__timeout_trigger_pythonNoExpires_setRedisTtl(self):
        # note: timeout-trigger will force python_expires
        session_args = self._args_timeout_trigger_noPythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[1][2], session_args['timeout'])

    def test_scenario_new__timeout_noTrigger_pythonExpires_setRedisTtl(self):
        session_args = self._args_timeout_noTrigger_pythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[1][2], session_args['timeout'])

    def test_scenario_new__timeout_noTrigger_noPythonExpires_setRedisTtl(self):
        """
        a timeout entirely occurs via EXPIRY in redis
        """
        session_args = self._args_timeout_noTrigger_noPythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[1][2], session_args['timeout'])

    # --------------------------------------------------------------------------
    # new session - no timeout
    # --------------------------------------------------------------------------

    def test_scenario_new__noTimeout_trigger_pythonExpires_setRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_pythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_trigger_pythonNoExpires_setRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_noPythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_noTrigger_pythonExpires_setRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_pythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_noTrigger_noPythonExpires_setRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_noPythonExpires_setRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    # --------------------------------------------------------------------------
    # existing session - timeout
    # --------------------------------------------------------------------------

    def test_scenario_existing__timeout_trigger_pythonExpires_setRedisTtl_noChange(self):
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__timeout_trigger_pythonNoExpires_setRedisTtl_noChange(self):
        # note: timeout-trigger will force python_expires

        session_args = self._args_timeout_trigger_noPythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__timeout_noTrigger_pythonExpires_setRedisTtl_noChange(self):
        session_args = self._args_timeout_noTrigger_pythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__timeout_noTrigger_noPythonExpires_setRedisTtl_noChange(self):
        """
        a timeout entirely occurs via EXPIRY in redis
        """
        session_args = self._args_timeout_noTrigger_noPythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    # --------------------------------------------------------------------------
    # existing session - timeout
    # --------------------------------------------------------------------------

    def test_scenario_existing__noTimeout_trigger_pythonExpires_setRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_pythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__noTimeout_trigger_pythonNoExpires_setRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_noPythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__noTimeout_noTrigger_pythonExpires_setRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_pythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    def test_scenario_existing__noTimeout_noTrigger_noPythonExpires_setRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_noPythonExpires_setRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request.registry._redis_sessions._history[0][2], session_args['timeout'])

    # ===========================
    # no ttl variants
    # ===========================

    def test_scenario_new__timeout_trigger_pythonExpires_noRedisTtl(self):
        session_args = self._args_timeout_trigger_pythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__timeout_trigger_pythonNoExpires_noRedisTtl(self):
        # note: timeout-trigger will force python_expires
        session_args = self._args_timeout_trigger_noPythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__timeout_noTrigger_pythonExpires_noRedisTtl(self):
        session_args = self._args_timeout_noTrigger_pythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__timeout_noTrigger_noPythonExpires_noRedisTtl(self):
        """
        a timeout entirely occurs via EXPIRY in redis
        """
        session_args = self._args_timeout_noTrigger_noPythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SETEX for the initial creation
        # 1 = a SETEX for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    # --------------------------------------------------------------------------
    # new session - no timeout
    # --------------------------------------------------------------------------

    def test_scenario_new__noTimeout_trigger_pythonExpires_noRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_pythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_trigger_pythonNoExpires_noRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_noPythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_noTrigger_pythonExpires_noRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_pythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    def test_scenario_new__noTimeout_noTrigger_noPythonExpires_noRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_noPythonExpires_noRedisTtl
        request = self._prep_new_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be two items in the history:
        # 0 = a pipeline.SET for the initial creation
        # 1 = a SET for the persist
        self.assertEqual(len(request.registry._redis_sessions._history), 2)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'pipeline.set')
        self.assertEqual(request.registry._redis_sessions._history[1][0], 'set')

    # --------------------------------------------------------------------------
    # existing session - timeout
    # --------------------------------------------------------------------------

    def test_scenario_existing__timeout_trigger_pythonExpires_noRedisTtl_noChange(self):
        session_args = self._args_timeout_trigger_pythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__timeout_trigger_pythonNoExpires_noRedisTtl_noChange(self):
        # note: timeout-trigger will force python_expires
        session_args = self._args_timeout_trigger_noPythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__timeout_noTrigger_pythonExpires_noRedisTtl_noChange(self):
        session_args = self._args_timeout_noTrigger_pythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertIn('x', stored_session_data)
        self.assertEqual(stored_session_data['x'], stored_session_data['c'] + stored_session_data['t'])

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__timeout_noTrigger_noPythonExpires_noRedisTtl_noChange(self):
        """
        a timeout entirely occurs via EXPIRY in redis
        """
        session_args = self._args_timeout_noTrigger_noPythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    # --------------------------------------------------------------------------
    # existing session - timeout
    # --------------------------------------------------------------------------

    def test_scenario_existing__noTimeout_trigger_pythonExpires_noRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_pythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__noTimeout_trigger_pythonNoExpires_noRedisTtl(self):
        """the ``timeout_trigger`` is irrelevant"""
        session_args = self._args_noTimeout_trigger_noPythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__noTimeout_noTrigger_pythonExpires_noRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_pythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    def test_scenario_existing__noTimeout_noTrigger_noPythonExpires_noRedisTtl(self):
        session_args = self._args_noTimeout_noTrigger_noPythonExpires_noRedisTtl
        request = self._prep_existing_session(session_args)

        # cookie_on_exception is True by default, no exception raised
        stored_session_data = self._deserialize_session_stored(request.session)
        self.assertNotIn('x', stored_session_data)

        # there should be 1 items in the history:
        # 0 = a SETEX for the initial creation
        self.assertEqual(len(request.registry._redis_sessions._history), 1)
        self.assertEqual(request.registry._redis_sessions._history[0][0], 'set')

    # --------------------------------------------------------------------------
    # new session - timeout flow
    # --------------------------------------------------------------------------

    def test_scenario_flow__timeout_trigger_pythonExpires_noRedisTtl(self):
        session_args = self._args_timeout_trigger_pythonExpires_noRedisTtl
        session_args['timeout'] = 100
        session_args['timeout_trigger'] = 50
        time_now = int_time()

        #
        # start by prepping the request
        #
        request1 = self._prep_existing_session(session_args)
        stored_session_data_1_pre = self._deserialize_session_stored(request1.session)

        # there should be 1 items in the history:
        # 0 = a SET for the initial creation
        self.assertEqual(len(request1.registry._redis_sessions._history), 1)
        self.assertEqual(request1.registry._redis_sessions._history[0][0], 'set')

        # let's adjust the timeout and make a request that won't change anything
        timeout_diff_1 = -9
        self._adjust_request_session(request1, test_adjust_expires=timeout_diff_1)
        stored_session_data_1_post = self._deserialize_session_stored(request1.session)
        self.assertIn('x', stored_session_data_1_post)
        self.assertEqual(stored_session_data_1_post['x'], stored_session_data_1_pre['x'] + timeout_diff_1)

        # there should still be 1 items in the history:
        # 0 = a SET for the initial creation
        self.assertEqual(len(request1.registry._redis_sessions._history), 1)
        self.assertEqual(request1.registry._redis_sessions._history[0][0], 'set')

        #
        # then make a second request.  we should not see a set, because we're within the timeout
        #
        request_unchanged = self._load_cookie_session_in_new_request(request_old=request1, **session_args)
        stored_session_data_unchanged = self._deserialize_session_stored(request_unchanged.session)

        self.assertIn('x', stored_session_data_unchanged)
        self.assertEqual(stored_session_data_unchanged['x'], stored_session_data_1_post['x'])

        # there should still be 1 items in the history:
        # 0 = a SET for the initial insert -- but it's not triggered by RedisSession
        # 0 = a SET for the update adjust -- which is triggered by RedisSession
        self.assertIs(request_unchanged.registry._redis_sessions, request1.registry._redis_sessions)
        self.assertEqual(len(request_unchanged.registry._redis_sessions._history), 1)
        self.assertEqual(request_unchanged.registry._redis_sessions._history[0][0], 'set')

        #
        # now make a substantial change on the backend
        #
        timeout_diff_2 = -50
        stored_session_data_2_pre = self._deserialize_session_stored(request_unchanged.session)
        self._adjust_request_session(request_unchanged, test_adjust_expires=timeout_diff_2)
        stored_session_data_2_post = self._deserialize_session_stored(request_unchanged.session)
        self.assertIn('x', stored_session_data_2_post)
        self.assertEqual(stored_session_data_2_post['x'], stored_session_data_2_pre['x'] + timeout_diff_2)

        #
        # this should trigger an update if we make a new request...
        #
        request_updated = self._load_cookie_session_in_new_request(request_old=request_unchanged, **session_args)
        stored_session_data_updated = self._deserialize_session_stored(request_updated.session)
        self.assertIn('x', stored_session_data_updated)
        self.assertEqual(stored_session_data_updated['x'], time_now + session_args['timeout'])

        # there should be 2 items in the history:
        # 0 = a SET for the initial insert -- but it's not triggered by RedisSession
        # 0 = a SET for the update adjust -- which is triggered by RedisSession
        self.assertIs(request_updated.registry._redis_sessions, request_unchanged.registry._redis_sessions)
        self.assertEqual(len(request_updated.registry._redis_sessions._history), 2)
        self.assertEqual(request_updated.registry._redis_sessions._history[0][0], 'set')
        self.assertEqual(request_updated.registry._redis_sessions._history[1][0], 'set')
        return

    def test_scenario_flow__timeout_trigger_pythonExpires_setRedisTtl(self):
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        session_args['timeout'] = 100
        session_args['timeout_trigger'] = 50
        time_now = int_time()

        #
        # start by prepping the request
        #
        request1 = self._prep_existing_session(session_args)
        stored_session_data_1_pre = self._deserialize_session_stored(request1.session)

        # there should be 1 items in the history:
        # 0 = a SET for the initial creation
        self.assertEqual(len(request1.registry._redis_sessions._history), 1)
        self.assertEqual(request1.registry._redis_sessions._history[0][0], 'setex')

        # let's adjust the timeout and make a request that won't change anything
        timeout_diff_1 = -9
        self._adjust_request_session(request1, test_adjust_expires=timeout_diff_1)
        stored_session_data_1_post = self._deserialize_session_stored(request1.session)
        self.assertIn('x', stored_session_data_1_post)
        self.assertEqual(stored_session_data_1_post['x'], stored_session_data_1_pre['x'] + timeout_diff_1)

        # there should still be 1 items in the history:
        # 0 = a SET for the initial creation
        self.assertEqual(len(request1.registry._redis_sessions._history), 1)
        self.assertEqual(request1.registry._redis_sessions._history[0][0], 'setex')

        #
        # then make a second request.  we should not see a setex, because we're within the timeout
        #
        request_unchanged = self._load_cookie_session_in_new_request(request_old=request1, **session_args)
        stored_session_data_unchanged = self._deserialize_session_stored(request_unchanged.session)

        self.assertIn('x', stored_session_data_unchanged)
        self.assertEqual(stored_session_data_unchanged['x'], stored_session_data_1_post['x'])

        # there should still be 1 items in the history:
        # 0 = a SET for the initial insert -- but it's not triggered by RedisSession
        # 0 = a SET for the update adjust -- which is triggered by RedisSession
        self.assertIs(request_unchanged.registry._redis_sessions, request1.registry._redis_sessions)
        self.assertEqual(len(request_unchanged.registry._redis_sessions._history), 1)
        self.assertEqual(request_unchanged.registry._redis_sessions._history[0][0], 'setex')

        #
        # now make a substantial change on the backend
        #
        timeout_diff_2 = -50
        stored_session_data_2_pre = self._deserialize_session_stored(request_unchanged.session)
        self._adjust_request_session(request_unchanged, test_adjust_expires=timeout_diff_2)
        stored_session_data_2_post = self._deserialize_session_stored(request_unchanged.session)
        self.assertIn('x', stored_session_data_2_post)
        self.assertEqual(stored_session_data_2_post['x'], stored_session_data_2_pre['x'] + timeout_diff_2)

        #
        # this should trigger an update if we make a new request...
        #
        request_updated = self._load_cookie_session_in_new_request(request_old=request_unchanged, **session_args)
        stored_session_data_updated = self._deserialize_session_stored(request_updated.session)
        self.assertIn('x', stored_session_data_updated)
        self.assertEqual(stored_session_data_updated['x'], time_now + session_args['timeout'])

        # there should be 2 items in the history:
        # 0 = a SET for the initial insert -- but it's not triggered by RedisSession
        # 0 = a SET for the update adjust -- which is triggered by RedisSession
        self.assertIs(request_updated.registry._redis_sessions, request_unchanged.registry._redis_sessions)
        self.assertEqual(len(request_updated.registry._redis_sessions._history), 2)
        self.assertEqual(request_updated.registry._redis_sessions._history[0][0], 'setex')
        self.assertEqual(request_updated.registry._redis_sessions._history[1][0], 'setex')
        return

    def test_scenario_flow__noCookie_a(self):
        """no cookie created when making a request"""
        # session_args should behave the same for all
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, **session_args)
        response = webob.Response()
        request._process_response_callbacks(response)
        request._process_finished_callbacks()
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 0)

    def test_scenario_flow__noCookie_b(self):
        """no cookie created when accessing a session attrib"""
        # session_args should behave the same for all
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, **session_args)
        v = request.session.get('foo', None)
        response = webob.Response()
        request._process_response_callbacks(response)
        request._process_finished_callbacks()
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 0)

    def test_scenario_flow__noCookie_c(self):
        """no cookie created when accessing a session_id"""
        # session_args should behave the same for all
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, **session_args)
        session_id = request.session.session_id
        response = webob.Response()
        request._process_response_callbacks(response)
        request._process_finished_callbacks()
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 0)

    def test_scenario_flow__cookie_a(self):
        """cookie created when setting a value"""
        # session_args should behave the same for all
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, **session_args)

        # session_id is non-existant on create
        session_id = request.session.session_id
        self.assertIs(session_id, LAZYCREATE_SESSION)
        request.session['a'] = 1

        # session_id is non-existant until necessary
        session_id = request.session.session_id
        self.assertIs(session_id, LAZYCREATE_SESSION)

        # insist this is necessary
        request.session.ensure_id()
        session_id = request.session.session_id
        self.assertIsNot(session_id, LAZYCREATE_SESSION)

        response = webob.Response()
        request._process_response_callbacks(response)
        request._process_finished_callbacks()
        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)

    def test_scenario_flow__cookie_b(self):
        """cookie created when setting a value"""
        # session_args should behave the same for all
        session_args = self._args_timeout_trigger_pythonExpires_setRedisTtl
        import webob
        request = self._make_request()
        request.session = self._makeOne(request, **session_args)

        # session_id is non-existant on create
        session_id = request.session.session_id
        self.assertIs(session_id, LAZYCREATE_SESSION)
        request.session['a'] = 1

        # session_id is non-existant until necessary
        session_id = request.session.session_id
        self.assertIs(session_id, LAZYCREATE_SESSION)

        response = webob.Response()
        request._process_response_callbacks(response)
        request._process_finished_callbacks()

        # session_id should have created after callbacks
        session_id = request.session.session_id
        self.assertIsNot(session_id, LAZYCREATE_SESSION)

        set_cookie_headers = response.headers.getall('Set-Cookie')
        self.assertEqual(len(set_cookie_headers), 1)


class TestRedisSessionFactory_loggedExceptions(_TestRedisSessionFactoryCore, _TestRedisSessionFactoryCore_UtilsNew):

    def _new_loggerData(self):
        return {'InvalidSession': 0,  # tested
                'InvalidSession_NoSessionCookie': 0,  # tested
                'InvalidSession_Lazycreate': 0,
                'InvalidSession_NotInBackend': 0,  # tested
                'InvalidSession_DeserializationError': 0,  # tested
                'InvalidSession_PayloadTimeout': 0,
                'InvalidSession_PayloadLegacy': 0,
                }

    def validate_loggerData(self, loggerData, **expected):
        for k, v in loggerData.items():
            if k not in expected:
                self.assertEqual(v, 0)
            else:
                self.assertEqual(v, expected[k])

    def _new_loggerFactory(self, func_invalid_logger=None, factory_args=None):
        if factory_args is None:
            factory_args = {}
        factory = RedisSessionFactory(
            'secret',
            func_invalid_logger=func_invalid_logger,
            **factory_args
        )
        return factory

    # -----

    def test_logger_InvalidSession_NoSessionCookie(self):

        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            assert isinstance(raised, InvalidSession)
            func_invalid_logger_counts['InvalidSession'] += 1
            assert isinstance(raised, InvalidSession_NoSessionCookie)
            func_invalid_logger_counts['InvalidSession_NoSessionCookie'] += 1

        factory = self._new_loggerFactory(func_invalid_logger=func_invalid_logger)

        request = self._make_request()
        redis = request.registry._redis_sessions
        session = factory(request)
        # validate
        self.validate_loggerData(func_invalid_logger_counts,
                                 InvalidSession=1,
                                 InvalidSession_NoSessionCookie=1,
                                 )

    # -----

    def test_logger_InvalidSession_NotInBackend(self):

        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            assert isinstance(raised, InvalidSession)
            func_invalid_logger_counts['InvalidSession'] += 1
            assert isinstance(raised, InvalidSession_NotInBackend)
            func_invalid_logger_counts['InvalidSession_NotInBackend'] += 1

        factory = self._new_loggerFactory(func_invalid_logger=func_invalid_logger)

        # this session isn't tied to our factory.
        request = self._make_request()
        redis = request.registry._redis_sessions

        self._set_session_cookie(request=request,
                                 session_id='no_backend')
        session = factory(request)
        # validate
        self.validate_loggerData(func_invalid_logger_counts,
                                 InvalidSession=1,
                                 InvalidSession_NotInBackend=1,
                                 )

    # -----

    def test_logger_InvalidSession_DeserializationError(self):
        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            assert isinstance(raised, InvalidSession)
            func_invalid_logger_counts['InvalidSession'] += 1
            assert isinstance(raised, InvalidSession_DeserializationError)
            func_invalid_logger_counts['InvalidSession_DeserializationError'] += 1

        session_args = {'timeout': 1,
                        'python_expires': True,
                        'set_redis_ttl': False,
                        }

        factory = self._new_loggerFactory(
            func_invalid_logger=func_invalid_logger,
            factory_args={'deserialized_fails_new': True,
                          }
        )
        request = self._prep_existing_session(session_args)
        redis = request.registry._redis_sessions
        assert 'existing_session' in redis.store

        # take of off the last 5 chars
        redis.store['existing_session'] = redis.store['existing_session'][:-5]

        # new request
        session = factory(request)
        # validate
        self.validate_loggerData(func_invalid_logger_counts,
                                 InvalidSession=1,
                                 InvalidSession_DeserializationError=1,
                                 )

    # -----

    def test_logger_InvalidSession_PayloadTimeout(self):
        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            assert isinstance(raised, InvalidSession)
            func_invalid_logger_counts['InvalidSession'] += 1
            assert isinstance(raised, InvalidSession_PayloadTimeout)
            func_invalid_logger_counts['InvalidSession_PayloadTimeout'] += 1

        session_args = {'timeout': 6,
                        'python_expires': True,
                        'set_redis_ttl': False,
                        }

        factory = self._new_loggerFactory(
            func_invalid_logger=func_invalid_logger,
            factory_args={'deserialized_fails_new': True,
                          }
        )
        request = self._prep_existing_session(session_args)
        redis = request.registry._redis_sessions
        assert 'existing_session' in redis.store

        # use the actual session's deserialize on the backend data
        deserialized = request.session.deserialize(redis.store['existing_session'])
        # make it 10 seconds earlier
        deserialized['x'] = deserialized['x'] - 10
        deserialized['c'] = deserialized['c'] - 10
        reserialized = request.session.serialize(deserialized)
        redis.store['existing_session'] = reserialized

        # new request, which should trigger a timeout
        session = factory(request)

        # validate
        self.validate_loggerData(func_invalid_logger_counts,
                                 InvalidSession=1,
                                 InvalidSession_PayloadTimeout=1,
                                 )
    # -----

    def test_logger_InvalidSession_PayloadLegacy(self):
        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            assert isinstance(raised, InvalidSession)
            func_invalid_logger_counts['InvalidSession'] += 1
            assert isinstance(raised, InvalidSession_PayloadLegacy)
            func_invalid_logger_counts['InvalidSession_PayloadLegacy'] += 1

        session_args = {'timeout': 6,
                        'python_expires': True,
                        'set_redis_ttl': False,
                        }

        factory = self._new_loggerFactory(
            func_invalid_logger=func_invalid_logger,
            factory_args={'deserialized_fails_new': True,
                          }
        )
        request = self._prep_existing_session(session_args)
        redis = request.registry._redis_sessions
        assert 'existing_session' in redis.store

        # use the actual session's deserialize on the backend data
        deserialized = request.session.deserialize(redis.store['existing_session'])

        # make it 1 version earlier
        deserialized['v'] = deserialized['v'] - 1
        reserialized = request.session.serialize(deserialized)
        redis.store['existing_session'] = reserialized

        # new request, which should trigger a legacy format issue
        session = factory(request)

        # validate
        self.validate_loggerData(func_invalid_logger_counts,
                                 InvalidSession=1,
                                 InvalidSession_PayloadLegacy=1,
                                 )

    def test_deserialized_error_raw(self):
        func_invalid_logger_counts = self._new_loggerData()

        def func_invalid_logger(request, raised):
            raise ValueError("this should not be run")

        factory = self._new_loggerFactory(
            func_invalid_logger=func_invalid_logger,
            factory_args={'deserialized_fails_new': False,
                          }
        )
        request = self._prep_existing_session({})
        redis = request.registry._redis_sessions
        assert 'existing_session' in redis.store

        # take of off the last 5 chars
        redis.store['existing_session'] = redis.store['existing_session'][:-5]

        # new request should raise a raw RawDeserializationError
        with self.assertRaises(RawDeserializationError) as cm_expected_exception:
            factory(request)

        exception_wrapper = cm_expected_exception.exception
        wrapped_exception = exception_wrapper.args[0]

        # we are using picke, so it should be exceptions.EOFError
        self.assertEqual(request.session.deserialize, cPickle.loads)
        self.assertIsInstance(exception_wrapper.args[0], EOFError)
