from django.http import HttpResponse
from django.test import TestCase
from shuup import configuration
from shuup.core.models import Shop
from shuup.xtheme import set_current_theme
from shuup.testing.factories import get_default_shop

from shuup_testutils.settings_base import SHUUP_DEFAULT_THEME


class SnakeTestCase(TestCase):
    @classmethod
    def set_up_class(cls):
        pass

    def set_up(self):
        pass

    @classmethod
    def init_shuup(cls):
        get_default_shop()
        set_current_theme(SHUUP_DEFAULT_THEME)
        configuration.set(Shop.objects.first(), 'setup_wizard_complete', True)

    def assert_true(self, expression, fail_message: str = None):
        return self.assertTrue(expression, msg=fail_message)

    def assert_false(self, expression, fail_message: str = None):
        return self.assertFalse(expression, msg=fail_message)

    def assert_equal(self, expected, actual, fail_message: str = None):
        return self.assertEqual(expected, actual, msg=fail_message)

    def assert_not_equal(self, expected, actual, fail_message: str = None):
        return self.assertNotEqual(expected, actual, fail_message)

    def assert_raises(self, exception_cls, callable_obj=None, *args, **kwargs):
        return self.assertRaises(exception_cls, callable_obj, *args, **kwargs)

    def assert_num_queries(self, *args, **kwargs):
        return self.assertNumQueries(*args, **kwargs)

    def assert_redirects(
        self,
        response: HttpResponse,
        expected_url: str,
        status_code: int = 302,
        target_status_code: int = 200,
        msg_prefix: str = '',
        fetch_redirect_response: bool = True,
    ):
        return self.assertRedirects(
            response, expected_url, status_code, target_status_code, None,
            msg_prefix, fetch_redirect_response,
        )

    def assert_contains(
        self,
        response: HttpResponse,
        text,
        count=None,
        status_code: int = 200,
        msg_prefix='',
        html=False,
    ):
        return self.assertContains(
            response,
            text,
            count=count,
            status_code=status_code,
            msg_prefix=msg_prefix,
            html=html,
        )

    def assert_not_contains(
        self,
        response,
        text,
        status_code=200,
        msg_prefix='',
        html=False,
    ):
        return self.assertNotContains(
            response,
            text,
            status_code=status_code,
            msg_prefix=msg_prefix,
            html=html,
        )

    def assert_in(self, member, container, msg: str = None):
        self.assertIn(member, container, msg)

    def assert_not_in(self, member, container, msg: str = None):
        self.assertNotIn(member, container, msg)

    def setUp(self):
        self.set_up()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_class()
