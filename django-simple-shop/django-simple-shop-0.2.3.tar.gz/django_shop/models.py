# coding=utf8
from __future__ import unicode_literals, absolute_import

import json
import os
import uuid
from operator import attrgetter
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.core.mail import send_mail
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Sum, Q, Count, Value
from django.db.models.functions import Coalesce
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField

from .utils import delivery
from .utils.payment import create_payment, get_payment


class PriorityModel(models.Model):
    PRIORITY_CHOICES = [(i, i) for i in range(-10, 10)]
    priority = models.IntegerField(
        'Приоритет', choices=PRIORITY_CHOICES, default=0,
        help_text='Чем выше приоритет, тем выше в списке появится объект'
    )

    class Meta:
        abstract = True
        ordering = ['-priority']


class ProductCategoryManager(models.Manager):
    def get_available(self):
        return self.get_all_available().filter(type=ProductCategory.TYPE_BASIC)

    def get_all_available(self):
        qs = self.filter(self.get_all_available_query()).distinct()
        return qs

    def get_all_available_query(self):
        return (
                   Q(
                       Q(products__is_unlimited=True) |
                       Q(products__always_visible=True) |
                       Q(products__entries__quantity__gt=0)
                   ) |
                   Q(
                       Q(children__products__is_unlimited=True) |
                       Q(children__products__always_visible=True) |
                       Q(children__products__entries__quantity__gt=0)
                   )
               ) & Q(is_hidden=False)


def get_upload_path(_, filename):
    _, ext = os.path.splitext(filename)
    date = datetime.utcnow()
    path = os.path.join('uploads', str(date.year), str(date.month),
                        uuid.uuid4().hex)
    return '{}{}'.format(path, ext)


class ProductCategory(PriorityModel):
    """Товарная категория, содержит в себе товары одного типа"""
    NON_IMPORTANT_FIELDS = ('description',)
    TYPE_BASIC = 'basic'
    TYPE_SECONDARY = 'secondary'
    TYPE_HOLIDAY = 'holiday'
    TYPE_BRAND = 'brand'
    TYPE_CHOICES = (
        (TYPE_BASIC, 'Базовая (в меню)'),
        (TYPE_SECONDARY, 'Вторичная (для группировки)'),
        (TYPE_HOLIDAY, 'Праздник'),
        (TYPE_BRAND, 'Бренд'),
    )

    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', verbose_name='Родительская категория', blank=True, null=True,
                               limit_choices_to={'type': TYPE_BASIC, 'parent': None}, related_name='children')
    description = models.TextField(verbose_name='Описание', blank=True)
    image = models.ImageField('Изображение',
                              upload_to=get_upload_path,
                              blank=True, null=True)

    type = models.CharField(max_length=20, verbose_name='Тип', choices=TYPE_CHOICES, default=TYPE_BASIC)
    is_hidden = models.BooleanField(
        'Спрятать', default=False, db_index=True,
        help_text='Спрятанные категории не отображаются вообще нигде'
    )

    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата последнего обновления', auto_now=True)

    objects = ProductCategoryManager()

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ('-priority', 'pk')
        permissions = (
            ("category_can_edit_important", "Can edit important fields"),
        )

    def __str__(self):
        return '{}/{}'.format(self.type, self.name)

    def products_ordered(self):
        """Получить упорядоченный по убыванию доступного остатка список товара
        в категории.

        В список попадают только те товары, которые есть в наличии или помечены
        как отображающиеся всегда.

        :rtype: list[Product]
        """
        return self.products.get_available().order_by('-in_stock', 'id')

    @cached_property
    def has_products(self):
        """Свойство: есть ли продукты в категории"""
        return self.products.exists()

    @cached_property
    def active_products_num(self):
        """Свойство: количество продуктов в наличии в категории"""
        return self.products.get_available().count()

    @cached_property
    def have_to_display(self):
        """Свойство: нужно ли отобразить категорию в списке"""
        return self.products.get_available().exists()

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})


class ProductCategoryCustomField(PriorityModel):
    """"""
    TYPE_BOOLEAN = 1
    TYPE_INTEGER = 2
    TYPE_DECIMAL = 3
    TYPE_STRING = 4
    FIELD_TYPE_CHOICES = (
        (TYPE_BOOLEAN, 'Да/Нет'),
        (TYPE_INTEGER, 'Целое число'),
        (TYPE_DECIMAL, 'Дробное число'),
        (TYPE_STRING, 'Строка до 500 символов'),
    )
    TYPE_HOOKS = {
        TYPE_BOOLEAN: lambda x: True if x == 'True' else False,
        TYPE_INTEGER: lambda x: int(x),
        TYPE_DECIMAL: lambda x: Decimal(x),
        TYPE_STRING: lambda x: x,
    }

    category = models.ForeignKey(ProductCategory, verbose_name='Категория',
                                 related_name='fields')

    name = models.CharField('Название', max_length=200)
    key = models.SlugField('Ключ', max_length=200)
    type = models.IntegerField('Тип значения', choices=FIELD_TYPE_CHOICES)
    choices = models.CharField(
        'Варианты выбора', max_length=1000, blank=True,
        help_text='Если у характеристики предполагается ограниченное число '
                  'значений, напишите их здесь через запятую'
    )
    required = models.BooleanField('Обязательное поле', default=False)
    hidden = models.BooleanField('Скрытое поле', default=False)
    is_filter = models.BooleanField('Поле-фильтр', default=False)

    class Meta:
        verbose_name = 'характеристика'
        verbose_name_plural = 'характеристики'
        ordering = ('-priority', 'pk')

    def __str__(self):
        return '{} ({})'.format(self.key, self.get_type_display())

    def value_from_raw_string(self, value):
        return self.TYPE_HOOKS[self.type](value)

    def valid_value_from_raw_string(self, value):
        try:
            return self.TYPE_HOOKS[self.type](value)
        except Exception:
            return ''

    @cached_property
    def choices_set(self):
        return {self.value_from_raw_string(x.strip())
                for x in self.choices.split(',')}

    @classmethod
    def validate_choices(cls, value_type, values):
        values = values.split(',')
        new_values = []
        for value in values:
            value = value.strip()
            if not value:
                raise ValidationError(
                    'Не допускаются пустые варианты выбора'
                )
            try:
                cls.TYPE_HOOKS[value_type](value)
            except (ValueError, InvalidOperation):
                raise ValidationError(
                    'Неверное значение в одном из вариантов выбора')
            new_values.append(value)
        return ', '.join(new_values)


class ProductManager(models.Manager):
    def get_available(self):
        return self.annotate(
            in_stock=Coalesce(Sum('entries__quantity'), Value(0))).filter(
                Q(is_unlimited=True) | Q(always_visible=True) |
                Q(in_stock__gt=0)
        )

    def get_by_value(self, fields_values, qs=None):
        q = Q()
        for field, value in fields_values.items():
            q |= (Q(custom_fields__value=value, custom_fields__field=field))
        if qs is None:
            qs = self.get_available()
        return qs.filter(q).annotate(Count('custom_fields')).filter(
            custom_fields__count=len(fields_values))


class Product(models.Model):
    NON_IMPORTANT_FIELDS = ('short_description', 'description')

    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(
        ProductCategory, verbose_name='Категории', related_name='products')

    price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Цена')
    old_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Старая цена',
        blank=True, null=True,
        help_text='Если старая цена указана, товар отображается как акционный'
    )
    weight = models.IntegerField(
        verbose_name='Вес',
        help_text='Масса единицы товара в упаковке (брутто) в граммах, '
                  'нужна для расчета стоимости доставки')
    width = models.IntegerField(
        'Ширина', help_text='Ширина упаковки единицы товара в миллиметрах'
    )
    depth = models.IntegerField('Глубина',
                                help_text='Глубина упаковки в миллиметрах')
    height = models.IntegerField('Высота',
                                 help_text='Высота упаковки в миллиметрах')

    is_new = models.BooleanField(
        'Новинка', default=True,
        help_text='Отображать товар как новинку'
    )
    is_unlimited = models.BooleanField(
        'Количество неорганичено', default=False, db_index=True,
        help_text='Если количество товара неограничено - для него не нужно '
                  'заводить поставки'
    )
    is_weight = models.BooleanField(
        default=False, verbose_name='Весовой товар',
        help_text='Весовой товар - это товар, которого можно приобрести '
                  'дробное количество'
    )
    measure = models.CharField(
        max_length=10, verbose_name='Единица измерения', blank=True,
        help_text='Обязательно заполнить, если товар весовой'
    )
    short_description = models.TextField(
        verbose_name='Короткое описание', blank=True,
        help_text='Описание, состоящее из одного абзаца текста, помещается '
                  'рядом с картинкой товара в каталоге.'
    )
    description = models.TextField(
        verbose_name='Полное описание', blank=True,
        help_text='Полное описание продукта, будет показано в его карточке.'
    )

    always_visible = models.BooleanField(
        'Виден всегда', default=False, db_index=True,
        help_text='Включите, если товар должен отображаться, даже если его '
                  'нет в наличии')

    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата последнего обновления', auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        permissions = (
            ("product_can_edit_important", "Can edit important fields"),
        )

    @cached_property
    def category(self):
        """Первая по приоритету категория товара"""
        res = None
        for cat in self.categories.all():
            if cat.is_hidden:
                continue
            if res is None:
                res = cat
            elif res.type == ProductCategory.TYPE_BASIC and cat.type != ProductCategory.TYPE_BASIC:
                continue
            elif res.type != ProductCategory.TYPE_BASIC and cat.type == ProductCategory.TYPE_BASIC:
                res = cat
            elif cat.priority > res.priority:
                res = cat
        return res

    @cached_property
    def primary_image(self):
        """Основное по приоритету изображение товара"""
        try:
            return self.images.all()[0].image
        except IndexError:
            return None

    @cached_property
    def in_stock(self):
        """Количество незабронированного товара на складе"""
        stock_amount = self.entries.filter(
            quantity__gt=0).aggregate(
            Sum('quantity')).get('quantity__sum') or 0
        reserved = self.orders.filter(
            order__state=Order.STATE_CREATED).aggregate(
            Sum('quantity')).get('quantity__sum') or 0
        if reserved > stock_amount:
            return 0
        return stock_amount - reserved
    in_stock.short_description = 'В наличии'

    @cached_property
    def volume(self):
        volume = Decimal('1')
        for attr in (self.width, self.height, self.depth):
            volume *= Decimal(attr) / Decimal('1000')
        return volume

    def check_fields(self):
        categories = self.categories.all()
        with transaction.atomic():
            fields_to_have = ProductCategoryCustomField.objects.filter(
                category__in=categories)
            current_fields = ProductCategoryCustomField.objects.filter(
                values__product=self)
            for field in fields_to_have:
                if field not in current_fields:
                    ProductCustomFieldValue.objects.create(product=self,
                                                           field=field)

    def get_absolute_url(self):
        if self.category is None:
            return '#'
        return reverse('shop:product', kwargs={'cat_slug': self.category.slug,
                                               'slug': self.slug})

    def create_copy(self):
        with transaction.atomic():
            obj = Product.objects.get(pk=self.pk)
            obj.name = 'Копия {}'.format(self.name)
            obj.slug = '{}-{}'.format(self.pk, self.slug)
            obj.pk = None
            obj.save()

            obj.categories.add(*tuple(self.categories.all()))
            fields = []
            for field in self.custom_fields.all():
                fields.append(ProductCustomFieldValue(
                    value=field.value, field=field.field, product=obj
                ))
            ProductCustomFieldValue.objects.bulk_create(fields)

    @cached_property
    def object_values(self):
        return self.custom_fields.all().select_related('field')


class ProductCustomFieldValue(models.Model):
    product = models.ForeignKey(Product, related_name='custom_fields')
    field = models.ForeignKey(ProductCategoryCustomField,
                              related_name='values')
    value = models.CharField(max_length=550, db_index=True, blank=True)

    class Meta:
        verbose_name = 'характеристика'
        verbose_name_plural = 'характеристики'
        unique_together = ('product', 'field')
        ordering = ('-field__priority', '-field__pk')

    def get_value_display(self):
        if self.field.type == self.field.TYPE_BOOLEAN:
            return 'Да' if self.value else 'Нет'
        return self.value


class ProductImage(PriorityModel):
    image = models.ImageField(
        upload_to=get_upload_path,
        verbose_name='Изображение',
        help_text='Изображение должно быть больше 600 пикселей по ширине'
    )
    product = models.ForeignKey(Product, related_name='images')

    class Meta:
        verbose_name = 'изображение продукта'
        verbose_name_plural = 'изображения продукта'
        ordering = ['-priority', 'pk']


class ProductEntry(models.Model):
    """Поставка товара на складе"""
    product = models.ForeignKey(Product, related_name='entries')
    quantity = models.DecimalField('Количество', max_digits=9,
                                   decimal_places=2, db_index=True)
    price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Стоимость')
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'поставка продукта'
        verbose_name_plural = 'поставки продукта'
        ordering = ['date']

    def __str__(self):
        return self.date.strftime('%c')


class PaymentType(PriorityModel):
    """Модель, задающая поддерживаемые магазином способы оплаты товара"""
    TYPE_OFFLINE = 1
    TYPE_ONLINE = 2
    TYPE_CHOICES = (
        (TYPE_OFFLINE, 'Оплата при получении'),
        (TYPE_ONLINE, 'Оплата онлаин')
    )

    name = models.CharField(
        max_length=200, verbose_name='Название',
        help_text='Короткое название способа оплаты'
    )
    description = models.TextField(
        verbose_name='Описание', blank=True,
        help_text='Короткое (в одно-два предложения) описание способа оплаты'
    )
    image = models.ImageField(
        'Изображение', upload_to=get_upload_path,
        blank=True, null=True
    )
    payment_type = models.IntegerField(
        verbose_name='Тип оплаты', choices=TYPE_CHOICES
    )
    payment_hook = models.CharField(
        verbose_name='Конкретный тип онлайн оплаты', max_length=50, blank=True
    )
    is_active = models.BooleanField(
        verbose_name='Используется', default=True,
        help_text='С помощью этой опции можно временно отключить способ '
                  'оплаты'
    )

    class Meta:
        verbose_name = 'способ оплаты'
        verbose_name_plural = 'способы оплаты'
        ordering = ['-priority']

    def __str__(self):
        return self.name

    def create_payment(self, order):
        """Создать объект платежа в Яндекс.Кассе если это нужно

        :type order: Order

        :rtype: yandex_money.models.Payment or None
        """
        if self.payment_type != self.TYPE_ONLINE:
            return

        return create_payment(self.payment_hook, order)

    def get_payment(self, order):
        if self.payment_type != self.TYPE_ONLINE:
            return

        return get_payment(self.payment_hook, order)


class DeliveryCity(models.Model):
    """Города, в которые поддерживается доставка"""
    TYPE_CITY = 'city'
    TYPE_TOWN = 'town'
    TYPE_CHOICES = (
        (TYPE_CITY, 'город'),
        (TYPE_TOWN, 'поселок'),
    )

    name = models.CharField('Название', max_length=200)
    region = models.CharField('Регион', max_length=200)
    district = models.CharField('Район', max_length=200)
    external_id = models.CharField('Код', max_length=11, db_index=True, unique=True)
    type = models.CharField('Тип', max_length=11, choices=TYPE_CHOICES)
    active = models.BooleanField('Активен', default=False)

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'города'

    def __str__(self):
        return '{} {}'.format(self.get_type_display(), self.name)


class DeliveryType(PriorityModel):
    """Модель, задающая поддерживаемые магазином способы доставки товара до
    покупателя"""

    SELECT_FULL = 'full'
    SELECT_LOCAL = 'local'
    SELECT_CONTACTS = 'contacts'
    SELECT_WIDGET = 'widget'
    ADDRESS_SELECT = (
        (SELECT_FULL, 'Ввод полного адреса'),
        (SELECT_LOCAL, 'Ввод локального адреса'),
        (SELECT_CONTACTS, 'Ввод контактов'),
        (SELECT_WIDGET, 'Ввод c помощью виджета'),
    )

    name = models.CharField(
        max_length=200, verbose_name='Название',
        help_text='Короткое название способа доставки'
    )
    description = models.TextField(
        verbose_name='Описание', blank=True,
        help_text='Короткое (в одно-два предложения) описание способа доставки'
    )
    image = models.ImageField(
        'Изображение', upload_to=get_upload_path,
        blank=True, null=True
    )
    pricing_method = models.CharField(
        verbose_name='Определение цены', max_length=30,
        choices=delivery.PRICING_METHODS,
        help_text='Способ вычисления цены доставки'
    )
    delivery_hook = models.CharField(
        verbose_name='Метод определения цены', max_length=30, blank=True,
        help_text='Задайте, если для получения цены и определения адреса '
                  'доставки используется отдельная логика'
    )
    address_select = models.CharField(
        verbose_name='Форма ввода адреса', max_length=30,
        choices=ADDRESS_SELECT, default=SELECT_FULL,
        help_text='Выбор вида отображаемой формы адреса'
    )
    min_delivery_time = models.IntegerField(
        verbose_name='Минимальное время доставки', default=0,
        help_text='Ожидаемое минимальное время доставки товара до пункта назначения'
    )
    city = models.ForeignKey(DeliveryCity, verbose_name='Город', limit_choices_to={'active': True},
                             blank=True, null=True)
    is_autogenerated = models.BooleanField('Сегенерирован автоматически', default=False, editable=False)
    options = models.TextField('Служебная информация', editable=False, blank=True, null=True)
    price = models.DecimalField(
        verbose_name='Цена', max_digits=9, decimal_places=2, blank=True,
        null=True,
        help_text='Цена доставки, указывается в случае, если для вычисления '
                  'цены используются методы "Заданная цена" и "Процент от '
                  'стоимости". Во втором случае нужно указать процент от '
                  'суммы покупки, который будет стоить доставка'
    )
    is_active = models.BooleanField(
        verbose_name='Используется', default=True,
        help_text='С помощью этой опции можно временно отключить способ '
                  'доставки'
    )

    class Meta:
        verbose_name = 'способ доставки'
        verbose_name_plural = 'способы доставки'
        ordering = ['-priority']

    def __str__(self):
        return self.name

    def actual_pricing(self):
        if self.pricing_method == delivery.METHOD_FREE:
            return
        elif self.pricing_method == delivery.METHOD_CONSTANT:
            return '{} руб.'.format(self.price)
        elif self.pricing_method == delivery.METHOD_PERCENT:
            return '{}%'.format(self.price)
        elif self.pricing_method == delivery.METHOD_API:
            return 'Цена расчетная'
        else:
            raise NotImplementedError
    actual_pricing.short_description = 'Цена'

    def price_display(self):
        if self.pricing_method == delivery.METHOD_FREE:
            return 'Бесплатно'
        elif self.pricing_method == delivery.METHOD_CONSTANT:
            return '{} &#8381;'.format(self.price)
        elif self.pricing_method == delivery.METHOD_PERCENT:
            return '{}% от стоимости товара'.format(self.price)
        elif self.pricing_method == delivery.METHOD_API:
            return 'Цена расчетная'
        else:
            raise NotImplementedError
    price_display.short_description = 'Цена'

    def get_price_and_address(self, options, address_form, order_price,
                              weight, measures):
        """Получить цену доставки и ее реальный адрес.

        Дополнительные данные о параметрах заказа нужны для засчета реальной
        цены в службе доставки

        :type options: str
        :param options: дополнительные параметры доставки
        :type address_form: dict[str, ANY]
        :param address_form: Данные об адресе доставки
        :type order_price: decimal.Decimal
        :param order_price: стоимость заказа
        :type weight: int
        :param weight: вес заказа в граммах
        :type measures: (int, int, int)
        :param measures: высота, ширина и глубина коробки, в которой поедет
            заказ

        :rtype: (decimal.Decimal, dict[str, ANY])
        :return: Цена доставки и ее реальный адрес
        """
        try:
            options = json.loads(options)
        except ValueError:
            options = {}
        options['hook'] = self.delivery_hook
        options['type_price'] = self.price
        return delivery.compute_price_and_address(
            self.pricing_method, options, address_form, order_price, weight,
            measures)

    def get_widget_scripts(self):
        if not self.delivery_hook or \
                self.address_select != self.SELECT_WIDGET:
            return ()
        return delivery.get_widget_scripts({'hook': self.delivery_hook})

    def get_options(self):
        return json.loads(self.options or '{}')

    def set_options(self, options):
        self.options = json.dumps(options)


class DeliveryAddress(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=300)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    phone = PhoneNumberField(verbose_name='Телефон')
    address = models.CharField(verbose_name='Адрес', max_length=500,
                               blank=True)
    city = models.CharField(verbose_name='Город/Населенный пункт',
                            max_length=200, blank=True)
    zip_code = models.CharField(verbose_name='Индекс', max_length=20,
                                blank=True)
    province = models.CharField(verbose_name='Регион/Облась', max_length=200,
                                blank=True)
    country = models.CharField(verbose_name='Страна', max_length=200,
                               blank=True)


class PackagingBox(models.Model):
    width = models.IntegerField(
        'Ширина', help_text='Ширина коробки в миллиметрах'
    )
    depth = models.IntegerField('Глубина',
                                help_text='Глубина коробки в миллиметрах')
    height = models.IntegerField('Высота',
                                 help_text='Высота коробки в миллиметрах')
    enabled = models.BooleanField('Используется', default=True)

    class Meta:
        verbose_name = 'формат упаковки'
        verbose_name_plural = 'форматы упаковки'

    def __str__(self):
        return '{}x{}x{}'.format(self.width, self.depth, self.height)

    @cached_property
    def volume(self):
        volume = Decimal('1')
        for attr in (self.width, self.height, self.depth):
            volume *= Decimal(attr) / Decimal('1000')
        return volume

    @classmethod
    def get_measures_for_products(cls, products):
        """Измерения прямоуголной коробки, в которую поместятся все продукты в
        корзине

        :type products: collections.Iterable[Product]
        """
        volume = sum(p.volume for p in products)
        volume *= Decimal('1.2')
        boxes = cls.objects.filter(enabled=True)
        for box in sorted(boxes, key=lambda b: b.volume):
            if box.volume > volume:
                return box.height, box.width, box.depth

        return 300, 300, 400


class Customer(models.Model):
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Последнее действие', auto_now=True)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return 'Клиент #{}'.format(self.pk)


class CustomersField(models.Model):
    TYPE_NAME = 'name'
    TYPE_PHONE = 'phone'
    TYPE_EMAIL = 'email'
    TYPE_IP = 'ip'
    TYPE_SESSION_ID = 'session_id'
    TYPE_YANDEX_ID = 'yandex_id'
    TYPE_GOOGLE_ID = 'google_id'
    TYPE_CHOICES = (
        (TYPE_NAME, 'Имя'),
        (TYPE_PHONE, 'Телефон'),
        (TYPE_EMAIL, 'Почта'),
        (TYPE_IP, 'IP'),
        (TYPE_SESSION_ID, 'Сессия'),
        (TYPE_YANDEX_ID, 'Yandex ID'),
        (TYPE_GOOGLE_ID, 'Google ID'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Клиент', related_name='fields')
    type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, db_index=True)
    value = models.CharField('Значение', max_length=200, db_index=True)
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'поле описания'
        verbose_name_plural = 'поля описания'

    def __str__(self):
        return self.value


class CustomersCart(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Клиент', related_name='carts')
    delivery_type = models.ForeignKey(
        DeliveryType, verbose_name='Способ доставки', null=True)
    payment_method = models.ForeignKey(
        PaymentType, verbose_name='Способ оплаты', null=True)
    name = models.ForeignKey(CustomersField, verbose_name='Имя', null=True, related_name='ncarts')
    phone = models.ForeignKey(CustomersField, verbose_name='Телефон', null=True, related_name='pcarts')
    email = models.ForeignKey(CustomersField, verbose_name='Email', null=True, related_name='ecarts')
    order = models.ForeignKey('Order', verbose_name='Заказ', null=True)
    created = models.DateTimeField('Дата первого действия', auto_now_add=True)
    updated = models.DateTimeField('Дата последнего изменения', auto_now=True)

    class Meta:
        verbose_name = 'корзина клиента'
        verbose_name_plural = 'корзины клиентов'
        ordering = ['-updated']

    def __str__(self):
        return 'Корзина #1'.format(self.id)


class ProductInCart(models.Model):
    cart = models.ForeignKey(CustomersCart, verbose_name='Заказ', related_name='products')
    product = models.ForeignKey(Product, verbose_name='Продукт')
    quantity = models.DecimalField('Количество', max_digits=9,
                                   decimal_places=1)

    class Meta:
        verbose_name = 'продукт в корзине'
        verbose_name_plural = 'продукты в корзине'

    def __str__(self):
        return str(self.product)


class CartActionLog(models.Model):
    ACTION_ADD = 'add'
    ACTION_SET = 'set'
    ACTION_REMOVE = 'remove'
    ACTION_DROP = 'drop'
    ACTION_SELECT_DELIVERY = 'delivery'
    ACTION_SELECT_PAYMENT = 'payment'
    ACTION_CHOICES = (
        (ACTION_ADD, 'Добавление в корзину'),
        (ACTION_SET, 'Установка количества'),
        (ACTION_REMOVE, 'Удаление из корзины'),
        (ACTION_DROP, 'Автоматическое удаление из корзины'),
        (ACTION_SELECT_DELIVERY, 'Выбор способа доставки'),
        (ACTION_SELECT_PAYMENT, 'Выбор способа оплаты'),
    )

    cart = models.ForeignKey(CustomersCart, verbose_name='Корзина', related_name='logs')
    action = models.CharField('Действие', choices=ACTION_CHOICES, max_length=10)
    message = models.CharField('Подробности', max_length=200)
    log_date = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        verbose_name = 'изменение корзины'
        verbose_name_plural = 'изменения корзины'
        ordering = ['-log_date']


class Order(models.Model):
    EMAIL_TEMPLATE_BASE = 'django_shop/email/order_{state}_{receiver}_{type}.txt'
    RECEIVER_MANAGER = 'manager'
    RECEIVER_CUSTOMER = 'customer'
    EMAIL_RECEIVERS = (RECEIVER_MANAGER, RECEIVER_CUSTOMER)
    EMAIL_TEMPLATE_TYPES = ('subject', 'body')

    STATE_CREATED = 'Created'
    STATE_CONFIRMED = 'Confirmed'
    STATE_DECLINED = 'Declined'
    STATE_SHIPPED = 'Shipped'
    STATE_DELIVERED = 'Delivered'
    STATE_REJECTED = 'Rejected'
    STATE_NC_CREATED = 'NCCreated'
    STATE_NC_PAID = 'NCPaid'
    STATE_NC_PAY_ERROR = 'NCPayError'
    STATE_NC_CONFIRMED = 'NCConfirmed'
    STATE_NC_DECLINED = 'NCDeclined'
    STATE_NC_SHIPPED = 'NCShipped'
    STATE_NC_DELIVERED = 'NCDelivered'
    STATE_NC_REJECTED = 'NCRejected'
    STATES = (
        (STATE_CREATED, 'Создан'),
        (STATE_CONFIRMED, 'Подтвержден'),
        (STATE_DECLINED, 'Не подтвержден'),
        (STATE_SHIPPED, 'Отправлен'),
        (STATE_DELIVERED, 'Доставлен'),
        (STATE_REJECTED, 'Отказ в получении'),
        (STATE_NC_CREATED, 'Создан (безнал)'),
        (STATE_NC_PAID, 'Оплачен (безнал)'),
        (STATE_NC_PAY_ERROR, 'Ошибка оплаты (безнал)'),
        (STATE_NC_CONFIRMED, 'Подтвержден (безнал)'),
        (STATE_NC_DECLINED, 'Не подтвержден (безнал)'),
        (STATE_NC_SHIPPED, 'Отправлен (безнал)'),
        (STATE_NC_DELIVERED, 'Доставлен (безнал)'),
        (STATE_NC_REJECTED, 'Отказ в получении (безнал)'),
    )
    STATES_DICT = {k: v for k, v in STATES}
    STATES_ORDERS = {
        STATE_CREATED: (STATE_CONFIRMED, STATE_DECLINED),
        STATE_CONFIRMED: (STATE_SHIPPED,),
        STATE_SHIPPED: (STATE_DELIVERED, STATE_REJECTED),
        STATE_NC_CREATED: (STATE_NC_PAY_ERROR,),
        STATE_NC_PAID: (STATE_NC_CONFIRMED, STATE_NC_DECLINED),
        STATE_NC_CONFIRMED: (STATE_NC_SHIPPED,),
        STATE_NC_SHIPPED: (STATE_NC_DELIVERED, STATE_NC_REJECTED),
    }

    uuid = models.UUIDField(verbose_name='Уникальный ключ', default=uuid.uuid4,
                            unique=True, editable=False)
    sid = models.CharField(verbose_name='ID клиента', editable=False,
                           max_length=50)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    changed = models.DateTimeField('Дата изменения', auto_now=True)
    state = models.CharField('Статус', max_length=50, choices=STATES,
                             default=STATE_CREATED)
    delivery_type = models.ForeignKey(
        DeliveryType, verbose_name='Способ доставки')
    delivery_price = models.DecimalField(max_digits=9, decimal_places=2,
                                         verbose_name='Стоимость доставки')
    delivery_address = models.ForeignKey(
        DeliveryAddress, verbose_name='Адрес доставки', editable=False)
    payment_method = models.ForeignKey(
        PaymentType, verbose_name='Способ оплаты', editable=False, null=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return 'Заказ №{}'.format(self.id)

    def get_absolute_url(self):
        return reverse('shop:order', kwargs={'uuid': self.uuid.hex})

    def get_state_choices(self):
        """Получить возможные варианты выбора статуса из текущего в формате
        choices
        """
        so = [self.state] + list(self.STATES_ORDERS.get(self.state, []))
        return [(s, self.STATES_DICT[s]) for s in so]

    def reduce_stock_amount(self):
        """Списать со склада товар в заказе"""
        for product in self._products.select_for_update():
            product.reduce_stock_amount()

    def _email_templates_for_state(self):
        for receiver in self.EMAIL_RECEIVERS:
            try:
                templates = []
                for email_type in self.EMAIL_TEMPLATE_TYPES:
                    templates.append(get_template(
                        self.EMAIL_TEMPLATE_BASE.format(
                            state=self.state.lower(), receiver=receiver,
                            type=email_type
                        ))
                    )
            except TemplateDoesNotExist:
                pass
            else:
                yield receiver, templates

    def send_emails(self):
        """Отправить письма клиентам и менеджерам, если это нужно в текущем
        статусе
        """
        for receiver, templates in self._email_templates_for_state():
            t_subject, t_message = templates
            if receiver == self.RECEIVER_MANAGER:
                receiver_list = [m[1] for m in settings.MANAGERS]
            else:
                if not self.delivery_address.email:
                    continue
                receiver_list = [self.delivery_address.email]

            subject = t_subject.render({'order': self})
            message = t_message.render({'order': self})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      receiver_list, fail_silently=True)

    def get_payment_complete_url(self, success):
        base_url = self.get_absolute_url()
        if self.payment_finished:
            return base_url
        if success:
            return base_url + '?success=1'
        else:
            return base_url + '?success=0'

    @classmethod
    def get_by_order_id(cls, order_id):
        try:
            return cls.objects.get(uuid=order_id)
        except cls.DoesNotExist:
            return

    @classmethod
    def from_forms(cls, products_form, order_form, receiver_form,
                   address_form, session_key):
        """Создать заказ из словарей с данными из набора форм"""
        dt = order_form['delivery_type']
        weight = sum(p['product'].weight * p['amount'] for p in products_form)
        order_price = sum(p['product'].price * Decimal(p['amount'])
                          for p in products_form)
        measures = PackagingBox.get_measures_for_products(
            p['product'] for p in products_form
        )
        price, addr = dt.get_price_and_address(order_form['delivery_options'],
                                               address_form,
                                               order_price, weight, measures)

        da = DeliveryAddress.objects.create(
            name=receiver_form['name'], email=receiver_form['email'],
            phone=receiver_form['phone'],
            address=addr.get('address', ''), city=addr.get('city', ''),
            zip_code=addr.get('zip_code', ''),
            province=addr.get('province', ''),
            country=addr.get('country', '')
        )

        pm = order_form['payment_type']
        state = cls.STATE_CREATED if pm.payment_type == pm.TYPE_OFFLINE else cls.STATE_NC_CREATED

        order = cls.objects.create(delivery_type=dt, delivery_price=price,
                                   delivery_address=da, sid=session_key,
                                   payment_method=pm, state=state)

        for pf in products_form:
            ProductOrder.objects.create(
                product=pf['product'], order=order, quantity=pf['amount'],
                price=pf['product'].price * Decimal(pf['amount'])
            )

        payment = pm.create_payment(order)
        order.payment = payment
        order.save()

        return order

    @cached_property
    def payment(self):
        """Объект платежа"""
        if self.payment_method is None:
            return None
        return self.payment_method.get_payment(self)

    @cached_property
    def payment_finished(self):
        """Платеж закончен (успешно или нет)"""
        if self.payment is None:
            return False
        return self.payment.is_completed

    @cached_property
    def payment_done(self):
        """Заказ успешно оплачен"""
        if self.payment is None:
            return False
        return self.payment.is_payed
    payment_done.boolean = True
    payment_done.short_description = 'Заказ оплачен'

    @cached_property
    def _products(self):
        ps = self.products.select_related('product')
        list(ps)
        return ps

    @cached_property
    def price(self):
        """Полная цена заказа без доставки"""
        return sum(map(attrgetter('price'), self._products))
    price.short_description = 'Стоимость товара'

    @cached_property
    def full_price(self):
        """Полная цена заказа с доставкой"""
        return self.price + self.delivery_price
    full_price.short_description = 'К оплате'

    @cached_property
    def products_string(self):
        products_data = []
        for product in self._products:
            if product.product.is_weight:
                measure = product.product.measure
            else:
                measure = 'шт'
            products_data.append(' - {} ({:.1} {});'.format(
                product.product.name, product.quantity, measure))
        return '\n'.join(products_data)
    products_string.short_description = 'Заказ'

    @cached_property
    def receiver(self):
        address_data = []
        for field in self.delivery_address._meta.fields:
            if field.name == 'id':
                continue
            data = getattr(self.delivery_address, field.name)
            if not data:
                continue
            address_data.append('{}: {}'.format(field.verbose_name, data))
        return '\n'.join(address_data)
    receiver.short_description = 'Информация о получателе'

    @cached_property
    def receiver_html(self):
        address_data = []
        for field in self.delivery_address._meta.fields:
            if field.name == 'id':
                continue
            data = getattr(self.delivery_address, field.name)
            if not data:
                continue
            if field.name == 'phone':
                format_str = '{0}: <a href="tel:{1}">{1}</a>'
            elif field.name == 'email':
                format_str = '{0}: <a href="mailto:{1}">{1}</a>'
            else:
                format_str = '{0}: {1}'
            address_data.append(format_str.format(field.verbose_name, data))
        return mark_safe('<br>'.join(address_data))
    receiver_html.short_description = 'Информация о получателе'

    def process_payment(self):
        if self.state in (self.STATE_NC_CREATED, self.STATE_NC_PAY_ERROR):
            self.state = self.STATE_NC_PAID
            self.save()

            self.reduce_stock_amount()
            self.send_emails()

    def process_payment_fail(self):
        if self.state == self.STATE_NC_CREATED:
            self.state = self.STATE_NC_PAY_ERROR
            self.save()

            self.reduce_stock_amount()


class ProductOrder(models.Model):
    """Товарная позиция в заказе"""

    product = models.ForeignKey(Product, related_name='orders')
    order = models.ForeignKey(Order, related_name='products')
    quantity = models.DecimalField('Количество', max_digits=9,
                                   decimal_places=2)
    price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Стоимость')
    stock_price = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name='Стоимость закупки',
                                      default=Decimal('0'))
    stock_reduced = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'

    def __str__(self):
        return str(self.product)

    @transaction.atomic
    def reduce_stock_amount(self):
        """Списать из доступного для продажи остатка количество товара в
        позиции
        """
        if self.stock_reduced:
            raise RuntimeError('Stock amount had already been reduced')

        self.stock_price = Decimal('0')
        if not self.product.is_unlimited:
            qs = self.product.entries.filter(
                quantity__gt=0).select_for_update()
            stock_amount = qs.aggregate(
                Sum('quantity')).get('quantity__sum') or 0

            if stock_amount < self.quantity:
                raise RuntimeError(
                    'На складе меньше товара, чем нужно (%s < %s)',
                    stock_amount, self.quantity)

            current_quantity = self.quantity

            for entry in qs:
                if entry.quantity >= current_quantity:
                    entry.quantity -= current_quantity
                    self.stock_price += entry.price * Decimal(current_quantity)
                    current_quantity = 0
                else:
                    current_quantity -= entry.quantity
                    self.stock_price += entry.price * Decimal(entry.quantity)
                    entry.quantity = 0

                entry.save()
                if not current_quantity:
                    break

        self.stock_reduced = True
        self.save()
