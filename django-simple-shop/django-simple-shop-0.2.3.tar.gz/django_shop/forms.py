from __future__ import unicode_literals, absolute_import

from collections import defaultdict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from functools import reduce

from .fields import ShopPhoneNumberField
from .models import Product, DeliveryType, PaymentType
from .signals import added_product_to_cart, set_product_amount_in_cart, removed_product_from_cart


class CartModifyForm(forms.Form):
    """Форма для изменения корзины в POST запросе"""
    ACTION_ADD = 'add'
    ACTION_REMOVE = 'remove'
    ACTION_SET = 'set'
    ACTIONS = (
        (ACTION_ADD, ACTION_ADD),
        (ACTION_REMOVE, ACTION_REMOVE),
        (ACTION_SET, ACTION_SET)
    )

    RESPONSE_FULL = 'full'
    RESPONSE_MINIMAL = 'minimal'
    RESPONSES = (
        (RESPONSE_FULL, RESPONSE_FULL),
        (RESPONSE_MINIMAL, RESPONSE_MINIMAL),
    )

    action = forms.ChoiceField(choices=ACTIONS)
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    amount = forms.DecimalField(min_value=0.1, required=False,
                                decimal_places=1)
    response = forms.ChoiceField(choices=RESPONSES)

    def clean_amount(self):
        if self.cleaned_data['amount'] is None:
            return
        return round(self.cleaned_data['amount'], 1)

    def clean(self):
        data = super(CartModifyForm, self).clean()
        if data.get('action') in (self.ACTION_SET, self.ACTION_ADD):
            if 'amount' not in data or not data['amount']:
                raise ValidationError(_('No amount data for action'),
                                      code='invalid')
        return data

    def perform_action(self, cart, request=None):
        """Выполнить действие формы над корзиной

        :type cart: django_shop.cart.Cart
        :param request: объект запроса
        """
        assert self.is_valid()
        if self.cleaned_data['action'] == self.ACTION_ADD:
            cart.add(self.cleaned_data['product'],
                     self.cleaned_data['amount'])
            added_product_to_cart.send(
                self, request=request, product=self.cleaned_data['product'],
                amount=self.cleaned_data['amount']
            )
        elif self.cleaned_data['action'] == self.ACTION_REMOVE:
            cart.remove(self.cleaned_data['product'])
            removed_product_from_cart.send(
                self, request=request, product=self.cleaned_data['product']
            )
        elif self.cleaned_data['action'] == self.ACTION_SET:
            cart.set(self.cleaned_data['product'],
                     self.cleaned_data['amount'])
            set_product_amount_in_cart.send(
                self, request=request, product=self.cleaned_data['product'],
                amount=self.cleaned_data['amount']
            )
        else:
            raise NotImplementedError('Action is not implemented')


class OrderForm(forms.Form):
    """Формирование заказа: общие данные о заказе, его тип доставки и оплаты"""
    payment_type = forms.ModelChoiceField(
        queryset=PaymentType.objects.filter(is_active=True),
        widget=forms.HiddenInput
    )
    delivery_type = forms.ModelChoiceField(
        queryset=DeliveryType.objects.filter(is_active=True),
        widget=forms.HiddenInput
    )
    delivery_options = forms.CharField(max_length=4000, required=False,
                                       widget=forms.HiddenInput)


class ReceiverForm(forms.Form):
    """Фомирование заказа: данные о покупателе"""
    name = forms.CharField(label='Ваше имя', max_length=300)
    phone = ShopPhoneNumberField(
        label='Ваш телефон',
        help_text='Введите ваш телефон в формате +7XXXXXXXXXX'
    )
    email = forms.EmailField(
        label='Ваш e-mail (необязательно)', required=False,
        help_text='Если вы укажите e-mail, мы будем отправлять '
                  'на него только сообщения о статусе заказа'
    )


class AddressForm(forms.Form):
    """Фомирование заказа: адрес покупателя"""
    address = forms.CharField(label='Адрес', max_length=500, required=False)
    city = forms.CharField(label='Город или Населенный пункт',
                           max_length=200, required=False,
                           widget=forms.HiddenInput)
    zip_code = forms.CharField(label='Индекс', max_length=20,
                               required=False,
                               widget=forms.HiddenInput)
    province = forms.CharField(label='Регион/Облась', max_length=200,
                               required=False,
                               widget=forms.HiddenInput)
    country = forms.CharField(label='Страна', max_length=200,
                              required=False,
                              widget=forms.HiddenInput)

    def clean(self):
        data = super(AddressForm, self).clean()
        # Если указан город - ожидаем, что адрес тоже передан
        if data.get('city'):
            if not data.get('address'):
                raise ValidationError('Не указан адрес')

        # Если указана страна, ожидаем, что нам передадут, город и индекс
        if data.get('country'):
            if not data.get('city'):
                raise ValidationError('Не указан город')
            elif not data.get('zip_code') and data['city'] != 'Санкт-Петербург':
                raise ValidationError('Не указан индекс')

        return data


class ProductOrderForm(forms.Form):
    """Фомирование заказа: информация о заказанном продукте"""
    product = forms.ModelChoiceField(queryset=Product.objects.all(),
                                     widget=forms.HiddenInput)
    amount = forms.DecimalField(min_value=0.1, decimal_places=1,
                                widget=forms.HiddenInput)

    def clean(self):
        data = super(ProductOrderForm, self).clean()
        if data.get('product') and data.get('amount'):
            product = data.get('product')
            if product.in_stock < data.get('amount') and \
                    not product.is_unlimited:
                raise ValidationError('Недостаточно товара на складе')

        return data


class ProductFilterForm(forms.Form):
    def __init__(self, category, fields, *args, **kwargs):
        super(ProductFilterForm, self).__init__(*args, **kwargs)

        self._category = category
        self._field_models = {}
        for field, values in fields:
            self._field_models[field.key] = (field, values)
            raw_values = set(
                map(lambda x: field.valid_value_from_raw_string(x),
                    (x.value for x in values))
            )
            if '' in raw_values:
                raw_values.remove('')
            if len(raw_values) <= 1:
                continue

            if field.type == field.TYPE_BOOLEAN:
                form_field = forms.NullBooleanField
            elif field.type == field.TYPE_INTEGER:
                form_field = forms.IntegerField
            elif field.type == field.TYPE_DECIMAL:
                form_field = forms.DecimalField
            elif field.type == field.TYPE_STRING:
                form_field = forms.CharField
            else:
                continue

            self.fields[field.key] = form_field(required=False,
                                                label=field.name)

            choices = [('', 'Все')]
            if field.type != field.TYPE_BOOLEAN:
                for choice in raw_values:
                    if choice != '':
                        choices.append((choice, str(choice)))
                self.fields[field.key].widget = forms.Select(
                    choices=choices)

    def filter_qs(self, qs):
        fields = defaultdict(set)
        for key, value in self.cleaned_data.items():
            if value is None:
                continue

            field, values = self._field_models[key]
            if field.type == field.TYPE_STRING and not value:
                continue

            for val in values:
                typed_val = field.valid_value_from_raw_string(val.value)
                if typed_val == value:
                    fields[field.pk].add(val.product_id)
        if not fields:
            return qs

        ids_list = reduce(lambda x, y: x & y, fields.values())
        return qs.filter(pk__in=ids_list)
