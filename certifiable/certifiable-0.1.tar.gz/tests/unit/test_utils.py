#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.utils` package."""

import os
import threading
import unittest
from decimal import Decimal

from mock import patch, Mock

from certifiable import CertifierTypeError, CertifierValueError, certify_bool, certify_bytes, \
    certify_date, certify_enum, certify_enum_value, certify_int, certify_number, certify_object, \
    certify_string, certify_text, certify_time, certify_timestamp
from certifiable.errors import CertifierParamError
from certifiable.utils import ENVVAR, _certify_int_param, certify_parameter, certify_required, \
    disable, enable, enable_from_env, is_enabled, make_certifier
from tests import TestError

funcs = [
    certify_bool,
    certify_bytes,
    certify_date,
    certify_enum,
    certify_enum_value,
    certify_int,
    certify_number,
    certify_object,
    certify_string,
    certify_text,
    certify_time,
    certify_timestamp,
]


class UtilsTestCase(unittest.TestCase):
    """Tests for `certifiable.utils` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        enable()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_make_certifier_baked_params(self):
        val = 987
        vector = dict(a=1, b='2')

        @make_certifier()
        def func(value, *args, **kwargs):
            assert value == val
            assert len(args) == 0
            assert kwargs == dict(vector)
            raise TestError()

        fn = func(**vector)
        self.assertRaises(TestError, fn, val)

    def test_make_certifier_no_baked_params(self):
        val = 987
        vector = dict(a=1, b='2')

        @make_certifier()
        def func(value, *args, **kwargs):
            assert value == val
            assert len(args) == 0
            assert kwargs == dict(vector)
            raise TestError()

        self.assertRaises(TestError, func, val, **vector)

    def test_certify_required(self):
        value = None
        required = True
        self.assertRaises(
            CertifierValueError,
            certify_required, value, required,
        )

        value = ''
        required = True
        certify_required(value, required)

    def test_certify_non_bool_raises_CertifierParamError(self):
        self.assertRaises(
            CertifierParamError,
            certify_required,
            True,
            required=123,
        )

    def test_certify_not_required(self):
        value = None
        required = False
        certify_required(value, required)

        value = 123
        required = False
        certify_required(value, required)

    def test_certify_parameter_required(self):
        _certify_int_param(
            None,
            required=False
        )
        self.assertRaises(
            CertifierTypeError,
            _certify_int_param,
            value=None,
            required=True
        )

    def test_certify_parameter_raises_CertifierParamsError(self):
        mock_certifier = Mock(side_effect=CertifierValueError('bang'))
        name = 'bob'
        value = 'smith'
        required = True

        self.assertRaises(
            CertifierParamError,
            certify_parameter,
            mock_certifier,
            name,
            value,
            dict(required=required),
        )
        mock_certifier.assert_called_once_with(value, required=required)

    def test_certify_parameter_int(self):
        _certify_int_param(
            123,
            required=True
        )

    def test_certify_parameter_fails(self):
        for i in [
            '123',
            4.5,
            Decimal(7),
        ]:
            self.assertRaises(
                CertifierTypeError,
                _certify_int_param,
                i,
                required=True,
            )

    def test__certify_int_param(self):
        pass

    def test_certify_params(self):
        pass


class UtilsEnablerTestCase(unittest.TestCase):
    """Tests for `certifiable.utils` enabler methods."""

    def setUp(self):
        """Set up test fixtures, if any."""
        enable()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_is_enabled(self):
        ise = is_enabled()
        disabled = not ise
        if disabled:
            enable()
            self.assertTrue(is_enabled())
            disable()
            self.assertFalse(is_enabled())
            enable()
            self.assertTrue(is_enabled())
        else:
            disable()
            self.assertFalse(is_enabled())
            enable()
            self.assertTrue(is_enabled())
            disable()
            self.assertFalse(is_enabled())

    def test_threads(self):
        ise = is_enabled()
        sem = threading.Semaphore(0)
        sem1 = threading.Semaphore(0)

        def fn(state):
            sem.acquire(blocking=True)
            if state:
                disable()
                self.assertFalse(is_enabled())
            else:
                enable()
                self.assertTrue(is_enabled())
            sem1.release()

        t = threading.Thread(
            target=fn,
            args=[ise],
        )
        t.setDaemon(True)
        t.start()
        sem.release()
        sem1.acquire(blocking=True)
        self.assertEqual(ise, is_enabled())

    def test_enable_from_env(self):
        ise = is_enabled()
        if ise:
            # Disable via env:
            os.environ[ENVVAR] = '0'
            enable_from_env()
            self.assertFalse(is_enabled())
            os.environ[ENVVAR] = '1'
            enable_from_env()
            self.assertTrue(is_enabled())
        else:
            # Enable via env:
            os.environ[ENVVAR] = '1'
            enable_from_env()
            self.assertTrue(is_enabled())
            os.environ[ENVVAR] = '0'
            enable_from_env()
            self.assertFalse(is_enabled())

    @patch('certifiable.utils.exec_func')
    def test_disabled_all(self, mock_exec):
        mock_exec.side_effect = TestError()

        enable()
        self.assertTrue(is_enabled())
        for fn in funcs:
            self.assertRaises(
                TestError,
                fn,
                None,
                required=True,
            )

        disable()
        self.assertFalse(is_enabled())
        for fn in funcs:
            self.assertIsNone(
                fn(
                    None,
                    required=True,
                ))

    def test_enable_from_env_non_bool(self):
        os.environ[ENVVAR] = 'bad-value'

        state = True
        self.assertTrue(enable_from_env(state))
        self.assertTrue(is_enabled())

        state = False
        self.assertFalse(enable_from_env(state))
        self.assertFalse(is_enabled())

        state = True
        self.assertTrue(enable_from_env(state))
        self.assertTrue(is_enabled())

    def test_no_non_required_value_all(self):
        enable()
        self.assertTrue(is_enabled())
        for fn in funcs + [certify_required]:
            self.assertIsNone(
                fn(
                    None,
                    required=False,
                ))


if __name__ == '__main__':
    unittest.main()
