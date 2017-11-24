from django import forms
from django.forms import BaseFormSet
from django.forms.formsets import DEFAULT_MIN_NUM, DEFAULT_MAX_NUM

from typing import Optional

from shuup.admin.form_part import TemplatedFormDef
from shuup.admin.form_part import FormPart
from shuup.core.models import Product

from attrim.models import Class, Option, Attribute


class AttributesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._cls = self.initial['cls'] # type: Class
        self._product = self.initial['product'] # type: Product
        self.name = self._cls.code # type: str
        
        self._define_options_field()

    def save(self):
        attr_lookups = {'cls': self._cls, 'product': self._product}
        if self.is_edit_form():
            attr = self._product.attrim_attrs.get(**attr_lookups)
        else:
            attr = Attribute.objects.create(**attr_lookups)
        attr.options.set(self.cleaned_data['options'])
        attr.save()

    def _define_options_field(self):
        if self.is_edit_form():
            options_initial = Attribute.objects.get(
                cls=self._cls, product=self._product,
            ).options.all()
        else:
            options_initial = []
        self.fields['options'] = forms.ModelMultipleChoiceField(
            required=False,
            queryset=Option.objects.filter(cls=self._cls),
            initial=options_initial,
            label='',
        )
    
    def is_edit_form(self) -> bool:
        attr_lookups = {'cls': self._cls, 'product': self._product}
        return self._product.attrim_attrs.filter(**attr_lookups).exists()


class AttributeFormSet(BaseFormSet):
    validate_min = False
    min_num = DEFAULT_MIN_NUM
    validate_max = False
    max_num = DEFAULT_MAX_NUM
    absolute_max = DEFAULT_MAX_NUM
    can_delete = False
    can_order = False
    extra = 0
    form = AttributesForm

    def __init__(self, *args, **kwargs):
        # need to pop out the shuup kwargs because the formset super.__init__()
        # can't accept them
        kwargs.pop('empty_permitted')
        kwargs.pop('prefix')
        kwargs.pop('files')
        super().__init__(*args, **kwargs)


class AttributesFormPart(FormPart):
    priority = 0
    name = 'attrim'
    formset = AttributeFormSet

    def get_form_defs(self) -> Optional[TemplatedFormDef]:
        if self._is_product_saved():
            yield TemplatedFormDef(
                name=self.name,
                form_class=self.formset,
                template_name='attrim/admin/product/attrim.jinja',
                required=False,
                kwargs={'initial': self._get_formset_initial_data()},
            )

    def form_valid(self, product_form):
        if self.name in product_form.forms:
            attrim_formset = product_form.forms[self.name]
            for attrim_form in attrim_formset:
                if attrim_form.has_changed():
                    attrim_form.save()

    def _get_formset_initial_data(self) -> list:
        formset_initial_data_list = []
        if self._is_product_has_type():
            product_type = self.object.type
            for attribute_cls in product_type.attrim_classes.all():
                form_initial_data = {
                    'cls': Class.objects.get(code=attribute_cls.code),
                    'product': self.object,
                }
                formset_initial_data_list.append(form_initial_data)
        return formset_initial_data_list

    def _is_product_saved(self) -> bool:
        if self.object.pk is None:
            return False
        else:
            return True

    def _is_product_has_type(self) -> bool:
        if self.object.type:
            return True
        else:
            return False
