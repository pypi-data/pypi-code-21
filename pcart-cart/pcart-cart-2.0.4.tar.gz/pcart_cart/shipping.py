from django import forms
from django.utils.translation import ugettext_lazy as _


class BaseShipping:
    title = None
    form_template = 'cart/shipping_form.html'

    def __init__(self, config={}):
        self.title = config.get('title', self.title)
        self.form_template = config.get('form_template', self.form_template)

    def get_title(self):
        return self.title

    def get_form_template(self, request):
        return self.form_template

    def get_form(self, request, *args, **kwargs):
        return None

    def render_data(self, data, plain_text=False):
        from django.utils.safestring import mark_safe
        _template = '<h4>%s</h4>'
        if plain_text:
            _template = '%s'
        return mark_safe(_template % self.get_title())


DEMO_CHOICES = [
    {
        'name': 'city',
        'label': _('City'),
        'choices': [
            'Poltava',
            'Kyiv',
            'Kharkiv',
        ],
    },
    {
        'name': 'office',
        'label': _('Office'),
        'related_with': 'city',
        'required': False,
        'choices': [
            ('Poltava office 1', 'Poltava'),
            ('Poltava office 2', 'Poltava'),
            ('Kyiv office', 'Kyiv'),
            ('Kharkiv office 1', 'Kharkiv'),
            ('Kharkiv office 2', 'Kharkiv'),
            ('Kharkiv office 3', 'Kharkiv'),
        ],
    },
    {
        'name': 'extra',
        'label': _('Extra'),
        'required': False,
    },
]


class ShippingWithParamsForm(forms.Form):
    def __init__(self, choices, *args, **kwargs):
        super(ShippingWithParamsForm, self).__init__(*args, **kwargs)
        field_choices = dict()
        _data = self.data.copy()
        for i in choices:
            if 'choices' in i:
                _choices = list()
                related_with = i.get('related_with')
                if not related_with:
                    for x in i['choices']:
                        _choices.append((x, x))
                else:
                    for x, tag in i['choices']:
                        if tag in field_choices[related_with]:
                            _choices.append((x, x))
                    field_choices[i['name']] = _choices

                if _choices:
                    if i['name'] in _data:
                        if _data.get(i['name']) in [x[0] for x in _choices]:
                            field_choices[i['name']] = [_data.get(i['name'])]
                        else:
                            _value = _choices[0][0]
                            field_choices[i['name']] = [_value]
                            _data[i['name']] = _value
                    else:
                        field_choices[i['name']] = [_choices[0][0]]

                self.fields[i['name']] = forms.ChoiceField(
                    label=i['label'],
                    choices=_choices,
                    required=i.get('required', True))
            else:
                self.fields[i['name']] = forms.CharField(label=i['label'], required=i.get('required', True))

        self.data = _data


class SimpleShipping(BaseShipping):
    title = _('Simple shipping method')


class WithParamsShipping(BaseShipping):
    def __init__(self, config={}):
        super(WithParamsShipping, self).__init__(config)
        self.choices = config.get('choices')

    def get_form(self, request, *args, **kwargs):
        if self.choices is not None:
            from django.utils.module_loading import import_string
            _choices = import_string(self.choices)
            form = ShippingWithParamsForm(_choices, *args, **kwargs)
            return form

    def render_data(self, data, plain_text=False):
        from django.template.loader import render_to_string

        context = {
            'method': self,
            'data': data,
        }
        if plain_text:
            return render_to_string('admin/cart/withparamsshipping_preview.txt', context)
        else:
            return render_to_string('admin/cart/withparamsshipping_preview.html', context)