from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from PIL import Image
from six import BytesIO

from .utils import delivery
from .utils.payment import get_model_choices
from .models import ProductCategoryCustomField


class ProductCategoryCustomFieldForm(forms.ModelForm):
    def clean(self):
        data = super(ProductCategoryCustomFieldForm, self).clean()
        if data.get('is_filter') and not data.get('choices') and \
                data.get('type') == ProductCategoryCustomField.TYPE_STRING:
            raise ValidationError('Фильтр по строкам может быть влючен только '
                                  'при указании вариантов выбора')
        if data.get('choices') and \
                data.get('type') == ProductCategoryCustomField.TYPE_BOOLEAN:
            raise ValidationError('Нельзя указывать выбор для таких полей')
        if data.get('choices') and data.get('type'):
            data['choices'] = ProductCategoryCustomField.validate_choices(
                data.get('type'), data.get('choices'))

        return data


class ProductImageAdminForm(forms.ModelForm):
    def clean_image(self):
        image = self.cleaned_data['image']
        if image is not None:
            im = Image.open(image)
            width, height = im.size
            if width < 600:
                raise ValidationError(
                    _('Image is to small: width (%(width)s) is lower than 600'),
                    code='invalid',
                    params={'width': width},
                )
            if image.name.endswith('png') and not hasattr(image, 'path'):
                im.convert('RGBA')
                new_img = Image.new("RGBA", im.size, "white")
                try:
                    new_img.paste(im, (0, 0), im)
                    f = BytesIO()
                    new_img.save(f, 'PNG')
                    image.file = f
                except ValueError:
                    pass
        return image


class ProductCustomFieldValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCustomFieldValueForm, self).__init__(*args, **kwargs)
        if self.instance.field_id is not None:
            t = self.instance.field.type
            required = self.instance.field.required
            choices = self.instance.field.choices.split(',')
            choices = list((v, v) for v in map(lambda x: x.strip(), choices))
            if not choices or choices == [('', '')]:
                choices = None
            initial = self.instance.value or None
            if t == ProductCategoryCustomField.TYPE_BOOLEAN:
                self.fields['value'] = forms.BooleanField(required=False, initial=initial)
            elif t == ProductCategoryCustomField.TYPE_INTEGER:
                self.fields['value'] = forms.IntegerField(required=required, initial=initial)
            elif t == ProductCategoryCustomField.TYPE_DECIMAL:
                self.fields['value'] = forms.DecimalField(required=required, initial=initial)
            elif t == ProductCategoryCustomField.TYPE_STRING:
                self.fields['value'] = forms.CharField(required=required, initial=initial)

            if choices:
                self.fields['value'].widget = forms.Select(choices=choices)

    def clean(self):
        data = super(ProductCustomFieldValueForm, self).clean()
        field = data.get('id')
        value = data.get('value')

        if value is None and not field:
            return data

        if not value and \
                field.field.type != ProductCategoryCustomField.TYPE_BOOLEAN and \
                not field.field.required:
            if value is None:
                data['value'] = ''
            return data

        data['value'] = str(value)
        return data


class PaymentTypeAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentTypeAdminForm, self).__init__(*args, **kwargs)
        self.fields['payment_hook'].widget = forms.Select(
            choices=get_model_choices())


class DeliveryTypeAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeliveryTypeAdminForm, self).__init__(*args, **kwargs)
        self.fields['delivery_hook'].widget = forms.Select(
            choices=delivery.get_model_choices())

    def clean(self):
        data = self.cleaned_data
        if 'pricing_method' not in data:
            return data

        if data['pricing_method'] in (delivery.METHOD_PERCENT,
                                      delivery.METHOD_CONSTANT):
            if not data.get('price'):
                raise ValidationError(
                    _('You need to enter price')
                )
        elif data['pricing_method'] == delivery.METHOD_API:
            if data.get('price'):
                raise ValidationError(
                    _('You should not enter price')
                )
            if not data.get('delivery_hook'):
                raise ValidationError(
                    _('You should provide pricing_hook')
                )
        elif data['pricing_method'] == delivery.METHOD_FREE:
            if data.get('price'):
                raise ValidationError(
                    _('You should not enter price')
                )
        return data
