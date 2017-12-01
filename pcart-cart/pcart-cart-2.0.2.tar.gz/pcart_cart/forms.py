from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.module_loading import import_string


def shipping_method_choices():
    shipping_methods = list()
    for m in settings.PCART_SHIPPING_METHODS:
        _shipping_method_class = import_string(m['backend'])
        _shipping_method = _shipping_method_class(config=m.get('config', {}))
        shipping_methods.append((m['name'], _shipping_method.get_title()))
    return shipping_methods


def payment_method_choices():
    payment_methods = list()
    for m in settings.PCART_PAYMENT_METHODS:
        _payment_method_class = import_string(m['backend'])
        _payment_method = _payment_method_class(config=m.get('config', {}))
        payment_methods.append((m['name'], _payment_method.get_title()))
    return payment_methods


class OrderCheckoutForm(forms.Form):
    name = forms.CharField(label=_('Name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    phone = forms.CharField(label=_('Phone'), required=True)

    shipping_method = forms.ChoiceField(label=_('Shipping method'), choices=shipping_method_choices)
    payment_method = forms.ChoiceField(label=_('Payment method'), choices=payment_method_choices)

    note = forms.CharField(label=_('Note'), widget=forms.Textarea, required=False)

    def clean_email(self):
        from pcart_customers.models import User
        email = self.cleaned_data['email']
        if self.customer.user is None:
            email_exists = User.objects.filter(email=email).exists()
            if email_exists:
                raise forms.ValidationError(_('A user with that email already exists.'))
        return email

    def clean_phone(self):
        from pcart_customers.models import User
        phone = self.cleaned_data['phone']
        if self.customer.user is None:
            phone_exists = User.objects.filter(phone=phone).exists()
            if phone_exists:
                raise forms.ValidationError(_('A user with that phone already exists.'))
        return phone

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer')
        super(OrderCheckoutForm, self).__init__(*args, **kwargs)
        if self.customer.user:
            if self.customer.name:
                self.fields['name'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['phone'].widget.attrs['readonly'] = True
