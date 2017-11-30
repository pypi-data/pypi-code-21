import os
import subprocess
import importlib

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from shuup import configuration
from shuup.core.models import Shop
from shuup.xtheme import set_current_theme
from shuup.testing.factories import get_default_shop

from shuup_testutils.settings_base import SHUUP_DEFAULT_THEME


class IntegrationTestCase(StaticLiveServerTestCase):
    #: to determine the absolute module path
    python_module_name = None  # type: str
    #: relative to the module dir, example: 'static/{django_app_name}/'
    yarn_dir = None  # type: str
    #: relative to the yarn_dir
    protractor_conf = 'tests/protractor.conf.js'
    server_address = 'localhost:8082'

    @classmethod
    def setUpClass(cls):
        cls.set_up_class_before()
        super().setUpClass()
        cls.set_up_class_after()

    @classmethod
    def set_up_class_after(cls):
        cls._check_config()
        cls._set_yarn_directory()
        cls.init_shuup()

    @classmethod
    def set_up_class_before(cls):
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = cls.server_address

    def run_protractor_tests(self):
        subprocess.run(['yarn', 'run', 'webdriver-manager', 'update'], check=True)
        subprocess.run(['yarn', 'run', 'protractor', self.protractor_conf], check=True)

    @classmethod
    def _check_config(cls):
        if not cls.yarn_dir or not cls.python_module_name:
            raise TestCaseConfigError(
                'the attributes yarn_dir and module_name are required.'
            )

    # noinspection PyShadowingBuiltins
    @classmethod
    def _set_yarn_directory(cls):
        module = importlib.import_module(cls.python_module_name)
        module_path = os.path.dirname(module.__file__)
        os.chdir(module_path + '/' + cls.yarn_dir)

    @classmethod
    def init_shuup(cls):
        cls._create_shop_without_maintenance_mode()
        call_command('shuup_init')
        set_current_theme(SHUUP_DEFAULT_THEME)
        configuration.set(Shop.objects.first(), 'setup_wizard_complete', True)

    @classmethod
    def _create_shop_without_maintenance_mode(cls):
        get_default_shop()


class TestCaseConfigError(Exception):
    pass
