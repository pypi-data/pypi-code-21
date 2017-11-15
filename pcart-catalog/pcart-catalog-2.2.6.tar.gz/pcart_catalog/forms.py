from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import BaseInlineFormSet
from parler.forms import TranslatableModelForm
from parler.widgets import SortedSelect, SortedSelectMultiple
from .models import (
    Product,
    Collection,
    ProductImage,
    ProductVariant,
    CollectionPluginModel,
    SimilarProductsPluginModel,
    PriceAggregationProfile,
)


def get_plugin_sorting_choices():
    from .settings import PCART_COLLECTION_ORDERINGS
    result = []
    for k in PCART_COLLECTION_ORDERINGS.keys():
        result.append((k, PCART_COLLECTION_ORDERINGS[k].get('label')))
    return result


def get_plugin_template_choices():
    from django.conf import settings
    result = []
    for k in settings.PCART_COLLECTION_TEMPLATES:
        if settings.PCART_COLLECTION_TEMPLATES[k].get('plugins_only', False):
            result.append((
                k,
                settings.PCART_COLLECTION_TEMPLATES[k].get('label') or
                settings.PCART_COLLECTION_TEMPLATES[k].get('template')
            ))
    return result


class EditCollectionForm(TranslatableModelForm):
    class Meta:
        model = Collection
        fields = '__all__'
        widgets = {
            # 'description': AdminPagedownWidget,
            'condition_product_types': SortedSelectMultiple,
            'condition_vendors': SortedSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        from .models import Vendor, ProductType
        from .settings import PCART_COLLECTION_TRIGGER_MODULES
        super(EditCollectionForm, self).__init__(*args, **kwargs)
        self.fields['condition_product_types'].queryset = ProductType.objects.all().prefetch_related('translations')
        self.fields['condition_vendors'].queryset = Vendor.objects.all().prefetch_related('translations')
        self.fields['trigger_module'] = forms.ChoiceField(
            choices=PCART_COLLECTION_TRIGGER_MODULES,
            label=_('Trigger module'),
        )


class AddProductForm(TranslatableModelForm):
    class Meta:
        model = Product
        fields = ['title', 'slug', 'product_type', 'status']


class EditProductForm(TranslatableModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'vendor': SortedSelect,
        }

    def __init__(self, *args, **kwargs):
        from .models import Vendor, ProductStatus, Collection
        super(EditProductForm, self).__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.all().prefetch_related('translations')
        self.fields['status'].queryset = ProductStatus.objects.all().prefetch_related('translations')
        self.fields['collections'].queryset = Collection.objects.all().prefetch_related('translations')
        if 'instance' in kwargs:
            obj = kwargs['instance']
            properties_fields = obj.get_properties_fields()
            for p in properties_fields:
                self.fields[p[0]] = p[2]

    def save(self, commit=True):
        instance = super(EditProductForm, self).save(commit=False)
        properties = {}
        properties_fields = instance.get_properties_fields()
        for p in properties_fields:
            _value = self.cleaned_data[p[0]]
            if _value:
                properties[p[1]] = _value
        instance.properties = properties
        if commit:
            instance.save()
        return instance


class EditProductImageForm(TranslatableModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {
            'html_snippet': forms.TextInput,
        }


class EditProductVariantForm(TranslatableModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        from .models import ProductStatus
        self.product_instance = kwargs.pop('product_instance')
        super(EditProductVariantForm, self).__init__(*args, **kwargs)
        self.fields['status'].queryset = ProductStatus.objects.all().prefetch_related('translations')
        initial_values = {}
        if 'instance' in kwargs:
            initial_values = kwargs['instance'].properties
        properties_fields = self.product_instance.get_properties_fields(initial_values=initial_values, for_variants=True)
        for p in properties_fields:
            self.fields[p[0]] = p[2]

    def save(self, commit=True):
        instance = super(EditProductVariantForm, self).save(commit=False)
        properties = self.product_instance.properties
        properties_fields = instance.get_properties_fields()
        for p in properties_fields:
            _value = self.cleaned_data[p[0]]
            if _value:
                properties[p[1]] = _value

        instance.properties = properties
        if commit:
            instance.save()
        return instance


class EditProductVariantFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(EditProductVariantFormSet, self).__init__(*args, **kwargs)
        self.form_kwargs['product_instance'] = kwargs['instance']


class PriceAggregationProfileForm(forms.ModelForm):
    model = PriceAggregationProfile

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        from .settings import PCART_PRICE_AGGREGATION_TEMPLATES
        from django.conf import settings as dj_settings
        super(PriceAggregationProfileForm, self).__init__(*args, **kwargs)
        self.fields['language'] = forms.ChoiceField(
            choices=dj_settings.LANGUAGES,
            label=_('Language'),
        )
        self.fields['template_name'] = forms.ChoiceField(
            choices=((k, v['label']) for k, v in PCART_PRICE_AGGREGATION_TEMPLATES.items()),
            label=_('Template name'),
        )


class CollectionPluginForm(forms.ModelForm):
    model = CollectionPluginModel

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CollectionPluginForm, self).__init__(*args, **kwargs)
        self.fields['sorting'] = forms.ChoiceField(
            choices=get_plugin_sorting_choices(),
            label=_('Sorting'),
        )
        self.fields['template_name'] = forms.ChoiceField(
            choices=get_plugin_template_choices(),
            label=_('Template name'),
        )


class SimilarProductsPluginForm(forms.ModelForm):
    model = SimilarProductsPluginModel

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SimilarProductsPluginForm, self).__init__(*args, **kwargs)
        self.fields['sorting'] = forms.ChoiceField(
            choices=get_plugin_sorting_choices(),
            label=_('Sorting'),
        )
        self.fields['template_name'] = forms.ChoiceField(
            choices=get_plugin_template_choices(),
            label=_('Template name'),
        )
