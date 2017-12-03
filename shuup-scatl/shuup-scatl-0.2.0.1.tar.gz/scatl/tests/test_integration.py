from unittest import skipIf

from attrim.models.type import Type
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr
from shuup.xtheme import set_current_theme
from shuup_testutils.cases import IntegrationTestCase

from scatl.apps import AppConfig
from scatl.tests.testproject.settings import IS_SKIP_INTEGRATION_TEST
from scatl.tests.testproject.settings import SHUUP_SCATL_TEST_THEME


class IntegrationTest(IntegrationTestCase):
    python_module_name = AppConfig.name
    yarn_dir = 'static/{}'.format(AppConfig.name)
    protractor_conf = 'protractor.conf.js'
    server_address = 'localhost:8082'

    @skipIf(IS_SKIP_INTEGRATION_TEST == True, 'The env var is setted to skip the tests.')
    def test(self):
        set_current_theme(SHUUP_SCATL_TEST_THEME)
        self._gen_mock_data()
        super().run_protractor_tests()

    def _gen_mock_data(self):
        gen = ModelsGen()
        
        product_kas = gen.product(name='KAS', price=1400)
        product_nod = gen.product(name='Node 32', price=1100)
        product_ava = gen.product(name='Avast', price=900)

        cls_lang = gen.attrim.cls(
            code='language',
            name='Language',
            type=Type.TRANS_STR,
            options_amount=0,
        )
        cls_l_o_sw = gen.attrim.option(
            cls=cls_lang, value=TransStr(en='swedish'), order=0,
        )
        cls_l_o_en = gen.attrim.option(
            cls=cls_lang, value=TransStr(en='english'), order=1,
        )
        cls_l_o_ua = gen.attrim.option(
            cls=cls_lang, value=TransStr(en='ukrainian'), order=2,
        )
        cls_l_o_gr = gen.attrim.option(
            cls=cls_lang, value=TransStr(en='german'), order=3,
        )
        cls_l_o_bg = gen.attrim.option(
            cls=cls_lang, value=TransStr(en='bulgarian'), order=4,
        )
        product_kas_l_attr = product_kas.attrim_attrs.create(cls=cls_lang)
        product_kas_l_attr.options.set([cls_l_o_en, cls_l_o_ua, cls_l_o_gr])
        product_nod_l_attr = product_nod.attrim_attrs.create(cls=cls_lang)
        product_nod_l_attr.options.set([cls_l_o_en, cls_l_o_sw, cls_l_o_bg])
        product_ava_l_attr = product_ava.attrim_attrs.create(cls=cls_lang)
        product_ava_l_attr.options.set([cls_l_o_en, cls_l_o_sw, cls_l_o_ua])

        cls_license_num = gen.attrim.cls(
            code='license_num',
            name='Number of licenses',
            type=Type.INT,
            options_amount=0,
        )
        cls_lm_o_1 = gen.attrim.option(cls=cls_license_num, value=1, order=0)
        cls_lm_o_2 = gen.attrim.option(cls=cls_license_num, value=2, order=1)
        cls_lm_o_3 = gen.attrim.option(cls=cls_license_num, value=3, order=2)
        cls_lm_o_4 = gen.attrim.option(cls=cls_license_num, value=4, order=3)
        cls_lm_o_5 = gen.attrim.option(cls=cls_license_num, value=5, order=4)
        cls_lm_o_6 = gen.attrim.option(cls=cls_license_num, value=6, order=5)
        product_kas_lm_attr = product_kas.attrim_attrs.create(cls=cls_license_num)
        product_kas_lm_attr.options.set([cls_lm_o_1, cls_lm_o_5, cls_lm_o_6])
        product_nod_lm_attr = product_nod.attrim_attrs.create(cls=cls_license_num)
        product_nod_lm_attr.options.set([cls_lm_o_1, cls_lm_o_2, cls_lm_o_3])
        product_ava_lm_attr = product_ava.attrim_attrs.create(cls=cls_license_num)
        product_ava_lm_attr.options.set([
            cls_lm_o_1, cls_lm_o_2, cls_lm_o_3, cls_lm_o_4, cls_lm_o_5,
            cls_lm_o_6,
        ])
