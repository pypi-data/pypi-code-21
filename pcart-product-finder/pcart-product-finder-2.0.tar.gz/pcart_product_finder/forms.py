from django import forms
from .models import ProductFinderFormPluginModel


EMPTY_ITEM = ('', '-----')


class ProductFinderForm(forms.Form):
    vendor = forms.ChoiceField(required=False, choices=(EMPTY_ITEM,))
    model = forms.ChoiceField(required=False, choices=(EMPTY_ITEM,))
    year = forms.ChoiceField(required=False, choices=(EMPTY_ITEM,))
    variant = forms.ChoiceField(required=False, choices=(EMPTY_ITEM,))

    def __init__(self, *args, **kwargs):
        from .models import ObjectVendor, ProductFinderConfig
        self.collection = kwargs.pop('collection')
        super(ProductFinderForm, self).__init__(*args, **kwargs)

        _config = ProductFinderConfig.objects.first()

        self.fields['vendor'].choices = (EMPTY_ITEM,) + \
            tuple((x['id'], x['title']) for x in ObjectVendor.objects.all().values('id', 'title'))
        vendor = model = generation = None
        if self.data.get('vendor'):
            vendor = ObjectVendor.objects.get(pk=self.data['vendor'])
            self.fields['model'].choices = (EMPTY_ITEM,) + \
                tuple((x['id'], x['title']) for x in vendor.models.all().values('id', 'title'))
        else:
            self.fields['model'].widget.attrs['readonly'] = True
            self.fields['year'].widget.attrs['readonly'] = True
            self.fields['variant'].widget.attrs['readonly'] = True

        if self.data.get('model'):
            model = vendor.models.get(pk=self.data['model'])
            years = set()
            years_choices = [EMPTY_ITEM]
            generations = model.generations.all()
            for g in generations:
                for i, x in enumerate(range(g.start_production, g.finish_production-1)):
                    if x not in years:
                        years_choices.append(('%s:%s' % (g.pk, i), str(x)))
                    years.add(x)
            self.fields['year'].choices = years_choices
        else:
            self.fields['year'].widget.attrs['readonly'] = True
            self.fields['variant'].widget.attrs['readonly'] = True

        if self.data.get('year'):
            generation = model.generations.get(pk=self.data['year'].split(':')[0])
            self.fields['variant'].choices = (EMPTY_ITEM,) + \
                  tuple((x['id'], x['title']) for x in generation.variants.all().values('id', 'title'))
        else:
            self.fields['variant'].widget.attrs['readonly'] = True

        if _config:
            self.fields['vendor'].label = _config.vendor_title
            self.fields['model'].label = _config.model_title
            self.fields['year'].label = _config.generation_title
            self.fields['variant'].label = _config.variant_title


class ProductFinderFormPluginForm(forms.ModelForm):
    model = ProductFinderFormPluginModel

    class Meta:
        fields = '__all__'
