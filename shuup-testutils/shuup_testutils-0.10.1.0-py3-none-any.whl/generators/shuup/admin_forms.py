from typing import List

from bs4 import BeautifulSoup
from django.core.urlresolvers import reverse
from django.test import Client
from shuup.core.models import ProductMediaKind
from shuup.core.models import Shop
from shuup.testing.factories import get_default_shop, get_default_tax_class, \
    get_default_product_type, get_default_sales_unit
from shuup_utils.settings import LANG_CODES, DEFAULT_LANG

from shuup_testutils.cases.clients import AuthAdminClient


class ShuupProductAdminFormsGen:
    def __init__(
        self,
        product_pk: int = None,
        client: Client = None,
        shop: Shop = None,
    ):
        self._client = client or AuthAdminClient()
        self._shop = shop or get_default_shop()
        self._form = self._collect_form_from_dom(
            dom=self._get_product_edit_page_dom(product_pk),
        )

    def get_form(self) -> dict:
        return self._form
    
    # TODO rename the kwargs into name and value
    def set_field(self, field_name: str, field_value: str):
        self._form.update({field_name: field_value})
    
    def set_name_field(self, name_new: str):
        name_input_name = 'base-name__{}'.format(DEFAULT_LANG)
        self._form.update({name_input_name: name_new})
    
    def set_price_field(self, price: int):
        price_input_name = 'shop{}-default_price_value'.format(self._shop.pk)
        self._form.update({price_input_name: price})
    
    def set_barcode_field(self, barcode_new: str):
        barcode_input_name = 'base-barcode'
        self._form.update({barcode_input_name: barcode_new})
    
    def set_image_fields(self, image_ids: List[int]):
        forms_count_with_default_one = int(self._form['images-TOTAL_FORMS'])
        forms_count_actual = forms_count_with_default_one - 1
        number_of_new_images = len(image_ids)
        forms_count_new = forms_count_actual + number_of_new_images
        self._form.update({'images-TOTAL_FORMS': forms_count_new})
        
        for image_index, image_id in enumerate(image_ids):
            image_form_number = forms_count_actual + image_index
            self.set_image_field(image_number=image_form_number, image_id=image_id)
    
    def set_image_field(
        self,
        image_id: int,
        image_number: int = 0,
        is_logo: bool = False,
    ):
        image_form_prefix = 'images-{}-'.format(image_number)
        image_form_data = {
            image_form_prefix + 'kind': ProductMediaKind.IMAGE.value,
            image_form_prefix + 'file': image_id,
            image_form_prefix + 'ordering': image_number + 1,
            image_form_prefix + 'public': 'on',
            image_form_prefix + 'shops': self._shop.pk,
            image_form_prefix + 'is_primary': 'on' if is_logo else 'off',
            image_form_prefix + 'purchased': '',
            image_form_prefix + 'id': '',
        }
        
        for lang_code in LANG_CODES:
            title_input_name = image_form_prefix + 'title__{}'.format(lang_code)
            desc_input_name = image_form_prefix + 'description__{}'.format(lang_code)
            image_form_data.update({title_input_name: ''})
            image_form_data.update({desc_input_name: ''})
        
        self._form.update(image_form_data)
        
    def _collect_form_from_dom(self, dom: BeautifulSoup) -> dict:
        fields_input = self._collect_input_fields(dom)
        fields_select = self._collect_select_fields(dom)
        fields_select_multiple = self._collect_select_multiple_fields(dom)
        field_shop_visibility = self._collect_shop_visibility_field()
        
        form = {
            **fields_input, **fields_select, **fields_select_multiple,
            **field_shop_visibility,
        }
        self._fix_wrong_default_images_counter(form)
        return form
    
    def _get_product_edit_page_dom(self, product_pk: int = None) -> BeautifulSoup:
        is_user_wants_to_edit_existing_product = product_pk
        if is_user_wants_to_edit_existing_product:
            product_form_url = reverse(
                viewname='shuup_admin:shop_product.edit',
                kwargs={'pk': product_pk},
            )
        else:
            product_form_url = reverse('shuup_admin:shop_product.new')
        self._init_client()
        self._init_shuup()
        edit_page_response = self._client.get(product_form_url)
        edit_page_dom = BeautifulSoup(edit_page_response.content)
        return edit_page_dom

    def _init_client(self):
        if type(self._client) is AuthAdminClient:
            self._client.init()
            self._client.login()

    def _init_shuup(self):
        """It'll create a set of required model for shuup."""
        get_default_tax_class()
        get_default_product_type()
        get_default_sales_unit()

    def _collect_input_fields(self, dom: BeautifulSoup) -> dict:
        inputs = {}
        form_inputs = dom.find_all('input', {'name': True})
        for form_input in form_inputs:
            input_name = form_input['name']
            input_value = form_input.get('value', '')
            inputs.update({input_name: input_value})
        return inputs
    
    def _collect_select_fields(self, dom: BeautifulSoup) -> dict:
        select_nodes = dom.find_all(
            name='select',
            attrs={'name': True, 'multiple': False},
        )
        select_fields = {}
        for select_node in select_nodes:
            select_option_selected = select_node.find('option', selected=True)
            if select_option_selected is not None:
                select_value = select_option_selected['value']
            else:
                select_value = ''
            
            select_name = select_node['name']
            select_fields.update({select_name: select_value})
        return select_fields
    
    def _collect_select_multiple_fields(self, dom: BeautifulSoup) -> dict:
        select_nodes = dom.find_all(
            name='select',
            attrs={'name': True, 'multiple': True},
        )
        select_fields = {}
        for select_node in select_nodes:
            select_options = select_node.find_all('option', selected=True)
            select_values = []
            for select_option in select_options:
                select_values.append(select_option['value'])
            
            select_name = select_node['name']
            
            select_fields.update({select_name: select_values})
        return select_fields
    
    def _collect_shop_visibility_field(self) -> dict:
        # I can't catch the input with BeautifulSoup
        input_name = 'shop{shop_pk}-visible'.format(shop_pk=self._shop.pk)
        input_value = 'on'
        shop_visibility_field = {input_name: input_value}
        return shop_visibility_field
    
    def _fix_wrong_default_images_counter(self, form: dict) -> dict:
        if not ('images-TOTAL_FORMS' in form):
            return form
        images_counter_wrong = int(form['images-TOTAL_FORMS'])
        images_counter_fixed = images_counter_wrong - 1
        form.update({'images-TOTAL_FORMS': images_counter_fixed})
        return form
