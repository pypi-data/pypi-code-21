import unittest

import mock

from cloudshell.devices.standards.validators import attr_length_validator


class TestValidators(unittest.TestCase):

    @mock.patch("cloudshell.devices.standards.validators.MAX_STR_ATTR_LENGTH", 2)
    def test_attr_length_validator(self):
        """Check that decorator will trim args and kwargs"""
        @attr_length_validator
        def tested_func(*args, **kwargs):
            return args, kwargs
        # act
        result = tested_func("arg", [], test_kwarg=u"kwarg", test_kwarg2={})
        # verify
        self.assertEqual(result, (("ar", []), {"test_kwarg": u"kw", "test_kwarg2": {}}))
