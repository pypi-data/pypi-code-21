# coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal


from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import python_2_unicode_compatible

from .client import BoxberryAPI
from .fields import JSONFieldCustom
from .signals import new_parsel_status


@python_2_unicode_compatible
class DeliveryAct(models.Model):
    act_id = models.CharField(verbose_name='Номер акта', max_length=20, null=True, blank=True)
    label = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    sticker = models.URLField(verbose_name='Ссылка на этикетки', null=True, blank=True)

    def __str__(self):
        return 'Акт передачи №{}'.format(self.act_id)

    class Meta:
        verbose_name = 'Акт передачи'
        verbose_name_plural = 'Акты передачи'

    def send_to_boxberry(self, commit=True, token=None, endpoint=None):
        bb_api = BoxberryAPI(token=token, endpoint=endpoint)

        response = bb_api.parsel_send(self.parsels.values_list('track', flat=True))

        self.act_id = response.get('id')
        self.label = response.get('label')
        self.sticker = response.get('sticker')
        if commit:
            self.save()

    def get_admin_change_url(self):
        url_name = 'admin:{app_label}_{model_name}_change'.format(
            app_label=self._meta.app_label,
            model_name=self._meta.model_name,
        )
        return reverse(url_name, args=(self.pk,))


@python_2_unicode_compatible
class Parsel(models.Model):
    DELIVERY_PVZ = 1
    DELIVERY_CUR = 2

    DELIVERY_TYPES = (
        (DELIVERY_PVZ, 'Самовывоз (доставка до ПВЗ)'),
        (DELIVERY_CUR, 'Курьерская доставка'),
    )

    label = models.URLField(verbose_name='Ссылка на скачивание PDF файла с этикетками', null=True, blank=True)
    delivery_act = models.ForeignKey(DeliveryAct, on_delete=models.PROTECT, verbose_name='Акт передачи',
                                     related_name='parsels', null=True, blank=True)
    comment = models.TextField(verbose_name='Комментарий боксберри', null=True, blank=True)

    # Общая информация о посылке
    track = models.CharField(verbose_name='Трекинг код', max_length=10, null=True, blank=True,
                             help_text='Если параметр будет не пустым, считается что вы хотите обновить ранее '
                                       'созданную посылку')
    order_id = models.CharField(verbose_name='Внутренний ID заказа', max_length=100, null=True, blank=True)
    pallet_number = models.CharField(verbose_name='Номер палеты', max_length=100, null=True, blank=True)
    price = models.DecimalField(verbose_name='Общая (объявленная) стоимость', max_digits=9, decimal_places=2)
    payment_sum = models.DecimalField(verbose_name='Сумма к оплате', max_digits=9, decimal_places=2, default=Decimal(0),
                                      help_text='Сумма, которую необходимо взять с получателя), руб')
    delivery_sum = models.DecimalField(verbose_name='Стоимость доставки', max_digits=9, decimal_places=2)
    delivery_type = models.PositiveSmallIntegerField(verbose_name='Тип доставки', choices=DELIVERY_TYPES)

    # Информация о пункте поступления и пункте выдачи
    pick_up_point = models.CharField(verbose_name='Код ПВЗ, в котором будет получен заказ', max_length=30, blank=True,
                                     help_text='Заполняется для самовывоза, для КД – оставить пустым', null=True)
    point_of_issue = models.CharField(verbose_name='Код пункта поступления ЗП', max_length=30,
                                      help_text='Код ПВЗ, в который ИМ сдаёт посылки для доставки. '
                                                'Заполняется всегда, не зависимо от вида доставки. '
                                                'Для ИМ, сдающих отправления на ЦСУ Москва заполняется значением 010')

    # Информация о получателе
    customer_fio = models.CharField(verbose_name='ФИО получателя ЗП', max_length=200, null=True, blank=True,
                                    help_text='Возможные варианты заполнения: «Фамилия Имя Отчество» или «Фамилия Имя» '
                                              '(разделитель – пробел). Внимание, для полностью предоплаченных заказов '
                                              'необходимо указывать Фамилию, Имя и Отчество получателя, т. к. при '
                                              'выдаче на ПВЗ проверяются паспортные данные.')

    phone = models.CharField(verbose_name='Номер мобильного телефона', max_length=20, null=True, blank=True,
                             help_text='В формате 9ХХХХХХХХХ (10 цифр, начиная с девятки)')
    phone2 = models.CharField(verbose_name='Доп. номер телефона', max_length=20, null=True, blank=True,
                              help_text='В формате 9ХХХХХХХХХ (10 цифр, начиная с девятки)')
    email = models.EmailField(verbose_name='E-mail для оповещений', null=True, blank=True)
    # Наименование юрлица-получателя
    ul_name = models.CharField(verbose_name='Наименование', max_length=250, null=True, blank=True)
    ul_address = models.TextField(verbose_name='Адрес', null=True, blank=True)
    ul_inn = models.CharField(verbose_name='ИНН', max_length=50, null=True, blank=True)
    ul_kpp = models.CharField(verbose_name='КПП', max_length=50, null=True, blank=True)
    ul_bik = models.CharField(verbose_name='БИК', max_length=50, null=True, blank=True)
    ul_r_s = models.CharField(verbose_name='Расчетный счет', max_length=50, null=True, blank=True)
    ul_kor_s = models.CharField(verbose_name='Кор. счет', max_length=50, null=True, blank=True)
    ul_bank_name = models.CharField(verbose_name='Наименование банка', max_length=150, null=True, blank=True)

    # Курьерская доставка
    cur_index = models.CharField(verbose_name='Индекс', max_length=100, null=True, blank=True)
    cur_city = models.CharField(verbose_name='Город', max_length=100, null=True, blank=True)
    cur_address = models.TextField(verbose_name='Адрес получателя', null=True, blank=True)
    cur_times_from_1 = models.TimeField(verbose_name='Время доставки, от', null=True, blank=True)
    cur_times_to_1 = models.TimeField(verbose_name='Время доставки, до', null=True, blank=True)
    cur_times_from_2 = models.TimeField(verbose_name='Альтернативное время доставки, от', null=True, blank=True)
    cur_times_to_2 = models.TimeField(verbose_name='Альтернативное время доставки, до', null=True, blank=True)
    cur_time_text = models.CharField(verbose_name='Время доставки текстовый формат', max_length=200, null=True,
                                     blank=True)
    cur_comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)

    # Информация по товарным позициям
    items = JSONFieldCustom(
        encoder=DjangoJSONEncoder,
        verbose_name='Блок с информацией по товарным позициям',
        help_text='[{"id": "Артикул товара в БД", "name": "Наименование товара", "UnitName": "Единица измерения", '
                  '"nds": "Процент НДС", "price": "Цена товара", "quantity": "Количество"}, ...]'
    )
    # Веса и баркоды
    weights = JSONFieldCustom(
        encoder=DjangoJSONEncoder,
        verbose_name='Веса и баркоды с 1 по 5 место (от 5 до 30000 г. на место)',
        help_text='{ "weight": 5, "weight2": 5, ... "weight5": 5 , "barcode": "1", ... "barcode5": "1"} weight должно '
                  'быть заполнено обязательно!, баркоды - опционально, но если у заполненных мест указан хотя бы один '
                  'баркод, то и остальные необходимо указать'
    )

    status_history = models.ManyToManyField('Status', through='StatusHistory', related_name='parsels')
    current_status = models.ForeignKey('StatusHistory', verbose_name='Текущий статус', related_name='current_parsel',
                                       null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.track)

    class Meta:
        verbose_name = 'Посылка'
        verbose_name_plural = 'Посылки'

    def delete(self, using=None, keep_parents=False, token=None, endpoint=None):
        bb_api = BoxberryAPI(token=token, endpoint=endpoint)
        response = bb_api.parsel_del(self.track)

        # Сначала убедимся, что мы удалили заказ в ББ
        if response.status_code != 200:
            raise Exception('Non 200 response from BB ({}): {}'.format(response.status_code, response.text))

        return super(Parsel, self).delete(using=using, keep_parents=keep_parents)

    def send_to_boxberry(self, commit=True, token=None, endpoint=None):
        bb_api = BoxberryAPI(token=token, endpoint=endpoint)

        response = bb_api.parsel_create_or_update(self.to_json())

        self.track = response['track']
        self.label = response['label']

        if commit:
            self.save()

    def update_status(self, token=None, endpoint=None):
        bb_api = BoxberryAPI(token=token, endpoint=endpoint)

        response = bb_api.list_statuses(self.track)

        for bb_status in response:
            status, _ = Status.objects.get_or_create(name=bb_status['Name'])

            sataus_created = timezone.datetime.strptime(bb_status['Date'], '%Y-%m-%dT%H:%M:%S')

            status_history_record, _ = StatusHistory.objects.get_or_create(
                parsel=self,
                status=status,
                comment=bb_status['Comment'],
                created=timezone.get_current_timezone().localize(sataus_created),
            )

    def to_json(self):
        data = {
            'updateByTrack': self.track,
            'order_id': self.order_id,
            'PalletNumber': self.pallet_number,
            # Общая (объявленная) стоимость ЗП, руб.
            'price': self.price,
            # Сумма к оплате (сумма, которую необходимо взять с получателя), руб
            'payment_sum': self.payment_sum,
            # Стоимость доставки
            'delivery_sum': self.delivery_sum,
            # Вид доставки: 1 – самовывоз, 2 - курьер
            'vid': self.delivery_type,
            'shop': {
                # Код пункта поступления ЗП
                'name1': self.point_of_issue,
            },
            # Информация о получателе
            'customer': {
                'fio': self.customer_fio,
                'phone': self.phone,
                'phone2': self.phone2,
                'email': self.email,
                'name': self.ul_name,
                'address': self.ul_address,
                'inn': self.ul_inn,
                'kpp': self.ul_kpp,
                'r_s': self.ul_r_s,
                'bank': self.ul_bank_name,
                'kor_s': self.ul_kor_s,
                'bik': self.ul_bik,
            },
            # Блок с информацией по товарным позициям
            'items': self.items,
            'weights': self.weights,
        }

        # Самовывоз ПВЗ
        if self.delivery_type == self.DELIVERY_PVZ:
            data['shop']['name'] = self.pick_up_point
        # Курьер
        else:
            data['kurdost'] = {
                'index': self.cur_index,
                # citi - не опечатка
                'citi': self.cur_city,
                'addressp': self.cur_address,
                'timesfrom1': self.cur_times_from_1.strftime('%H:%M') if self.cur_times_from_1 else None,
                'timesto1': self.cur_times_to_1.strftime('%H:%M') if self.cur_times_to_1 else None,
                'timesfrom2': self.cur_times_from_2.strftime('%H:%M') if self.cur_times_from_2 else None,
                'timesto2': self.cur_times_to_2.strftime('%H:%M') if self.cur_times_to_2 else None,
                'timep': self.cur_time_text,
                'comentk': self.cur_comment,
            }

        return data


@python_2_unicode_compatible
class Status(models.Model):

    name = models.CharField(verbose_name='Наименование', max_length=50)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


@python_2_unicode_compatible
class StatusHistory(models.Model):
    parsel = models.ForeignKey(Parsel, verbose_name='Посылка', on_delete=models.PROTECT)
    status = models.ForeignKey(Status, verbose_name='Статус', on_delete=models.PROTECT)
    created = models.DateTimeField(verbose_name='Дата')
    comment = models.TextField(verbose_name='Комментарий', default='')

    def __str__(self):
        return '{}'.format(self.status)

    class Meta:
        ordering = ('-created', '-id')

    def save(self, *args, **kwargs):
        super(StatusHistory, self).save(*args, **kwargs)

        # Отсылаем сигнал, если у посылки появились новые статусы
        new_parsel_status.send(sender=None, status=self)

        # Обновляем текущий статус посылки
        if not self.parsel.current_status or self.parsel.current_status.created < self.created:
            self.parsel.current_status = self
            self.parsel.save()
