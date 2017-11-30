from typing import List

from parler.utils.context import switch_language
from rest_framework.reverse import reverse
from shuup.testing.factories import get_default_product_type
from shuup_testutils.cases import ApiAuthAdminTestCase
from shuup_utils.lang_constants import LANG_CODES, DEFAULT_LANG

from attrim.models import Class, Option
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr
from attrim.models.type import Type


# TODO use a const in `reverse`
class ClsRestapiTest(ApiAuthAdminTestCase):
    def set_up(self):
        super().set_up()
        self.gen = ModelsGen()

    def test_create_invalid_with_name_in_default_lang(self):
        response = self.client.post(reverse('class-list'), format='json', data=dict(
            code='test_code',
            type=Type.INT,
            name=TransStr(en=''),
            product_type=get_default_product_type().pk,
        ))
        self.assert_equal(response.status_code, 400)
    
    def test_create_invalid_with_name_in_random_lang(self):
        response = self.client.post(reverse('class-list'), format='json', data=dict(
            code='test_code',
            type=Type.INT,
            name=TransStr(fi=''),
            product_type=get_default_product_type().pk,
        ))
        self.assert_equal(response.status_code, 400)
    
    def test_create_invalid_with_name_empty(self):
        response = self.client.post(reverse('class-list'), format='json', data=dict(
            code='test_code',
            type=Type.INT,
            name={},
            product_type=get_default_product_type().pk,
        ))
        self.assert_equal(response.status_code, 400)
    
    def test_create(self):
        cls_code = 'some_code'
        cls_name = self.gen.attrim.trans_str()
        cls_type = Type.TRANS_STR
        self.client.post(reverse('class-list'), format='json', data=dict(
            code=cls_code,
            type=cls_type,
            name=cls_name.as_dict(),
            product_type=get_default_product_type().pk,
        ))
        cls = Class.objects.get(code=cls_code)
        self.assert_equal(
            expected=cls_name.get_value_in_current_lang(),
            actual=cls.name,
        )
        self.assert_equal(cls_type, actual=cls.type)
        
        response = self.client.get('/api/attrim/classes/', content_type='text/html')
        self.assert_equal(response.status_code, 200)
    
    def test_get_detail(self):
        cls_name = self.gen.attrim.trans_str()
        cls = self.gen.attrim.cls(name=cls_name)
        
        response = self.client.get(reverse('class-detail', kwargs={'pk': cls.pk}))
        for lang_code in LANG_CODES:
            with switch_language(cls, lang_code):
                self.assert_contains(response, cls.name)
        self.assert_contains(response, cls.code)
    
    def test_add_options(self):
        cls_name = self.gen.attrim.trans_str()
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, name=cls_name, options_amount=0)
        option_list = self.gen.attrim.option_list(cls=cls) # type: List[Option]
        option_pk_list = [] # type: List[int]
        for option in option_list:
            option_pk_list.append(option.pk)
        
        cls_url = reverse('class-detail', kwargs={'pk': cls.pk})
        self.client.put(cls_url, format='json', data=dict(
            code=cls.code,
            type=cls.type,
            name=cls_name.as_dict(),
            product_type=get_default_product_type().pk,
            options=option_pk_list,
        ))
        
        cls = Class.objects.get(code=cls.code)
        option_pk_list_actual = [] # type: List[int]
        for option in cls.options.all():
            option_pk_list_actual.append(option.pk)
        self.assert_equal(option_pk_list, option_pk_list_actual)
    
    def test_update_name(self):
        cls_name = self.gen.attrim.trans_str() # type: TransStr
        cls = self.gen.attrim.cls(name=cls_name)
        
        cls_name_new_value = 'new name'
        cls_name_new = cls_name.copy() # type: TransStr
        cls_name_new[DEFAULT_LANG] = cls_name_new_value
        cls_url = reverse('class-detail', kwargs={'pk': cls.pk})
        self.client.put(cls_url, format='json', data=dict(
            code=cls.code,
            type=cls.type,
            name=cls_name_new.as_dict(),
            product_type=get_default_product_type().pk,
        ))
        cls = Class.objects.get(code=cls.code)
        self.assert_equal(
            expected=cls_name_new_value,
            actual=cls.name,
        )
