from unittest import skipIf

from django.contrib.auth import get_user_model
from shuup.testing.factories import get_default_tax_class
from shuup_testutils.cases import IntegrationTestCase

from attrim.apps import AppConfig
from attrim.models import Option
from attrim.models.type import Type
from attrim.tests.testproject.settings import IS_SKIP_INTEGRATION
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr


class IntegrationTest(IntegrationTestCase):
    python_module_name = AppConfig.name
    yarn_dir = 'static/{}/admin'.format(AppConfig.name)
    protractor_conf = 'protractor.conf.js'
    server_address = 'localhost:8082'

    @skipIf(IS_SKIP_INTEGRATION == True, 'The env var is setted to skip the tests.')
    def test_integration(self):
        self._gen_mock_data()
        super().run_protractor_tests()

    def _gen_mock_data(self):
        get_user_model().objects.create_superuser(
            username='test',
            email='test@localhost',
            password='test@localhost',
        )

        get_default_tax_class()

        gen = ModelsGen()
        gen.product()

        cls_lang = gen.attrim.cls(
            code='language',
            name=TransStr(
                en='Translations',
                fi='Translations fi',
            ),
            type=Type.TRANS_STR,
            options_amount=0,
        )
        Option.objects.create(cls=cls_lang, value=TransStr(en='english'), order=1)
        Option.objects.create(cls=cls_lang, value=TransStr(en='german'), order=2)
        Option.objects.create(cls=cls_lang, value=TransStr(en='finish'), order=3)
