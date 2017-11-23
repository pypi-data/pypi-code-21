# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect

from .admin_filters import LastStatusLIstFilter
from .models import DeliveryAct, Parsel, Status, StatusHistory


def send_to_boxberry(modeladmin, request, queryset):
    errors = ''
    success = []
    level = messages.INFO
    for instance in queryset:
        try:
            instance.send_to_boxberry()
        except Exception as e:
            errors += '{}: {}\n'.format(instance.pk, e)
        else:
            success.append(instance)

    msg = 'Успешно созданы: {}'.format(', '.join([str(item.id) for item in success])) if success else ''
    if errors:
        level = messages.ERROR
        msg += '\nОшибки:\n{}'.format(errors)

    modeladmin.message_user(request, msg, level=level)

send_to_boxberry.short_description = 'Создать в Боксберри'


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    readonly_fields = ('status', 'comment', 'created')
    extra = 0


@admin.register(Parsel)
class ParselAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'track', 'current_status')
    actions = [send_to_boxberry, 'update_status', 'to_act']
    search_fields = ('id', 'track')
    inlines = (StatusHistoryInline,)
    list_filter = ('current_status', 'delivery_type',)
    fieldsets = (
        (None, {
            'fields': ('delivery_act',)
        }),
        ('Сведения из ББ', {
            'fields': ('label', 'track')
        }),
        ('Общая информация о посылке', {
            'fields': ('order_id', 'pallet_number', 'price', 'payment_sum', 'delivery_sum', 'delivery_type',)
        }),
        ('Информация о пункте поступления и пункте выдачи', {
            'fields': ('pick_up_point', 'point_of_issue')
        }),
        ('Информация о получателе', {
            'fields': ('customer_fio', 'phone', 'phone2', 'email')
        }),
        ('Информация о получателе-юрлице', {
            'fields': ('ul_name', 'ul_address', 'ul_inn', 'ul_kpp', 'ul_bik', 'ul_r_s', 'ul_kor_s', 'ul_bank_name')
        }),
        ('Курьерская доставка', {
            'fields': ('cur_index', 'cur_city', 'cur_address', 'cur_times_from_1', 'cur_times_to_1', 'cur_times_from_2',
                       'cur_times_to_2', 'cur_time_text', 'cur_comment')
        }),
        ('Информация по товарным позициям', {
            'fields': ('items',)
        }),
        ('Веса и баркоды', {
            'fields': ('weights',)
        }),
    )

    def update_status(self, request, queryset):
        errors = ''
        success = []
        level = messages.INFO
        for instance in queryset.filter(track__isnull=False):
            try:
                instance.update_status()
            except Exception as e:
                errors += '{}: {}\n'.format(instance.pk, e)
            else:
                success.append(instance)

        msg = 'Успешно обновлены: {}'.format(', '.join([str(item.id) for item in success])) if success else ''
        if errors:
            level = messages.ERROR
            msg += '\nОшибки:\n{}'.format(errors)

        self.message_user(request, msg, level=level)

    update_status.short_description = 'Обновить статус'

    def to_act(self, request, queryset):

        # Проверяем, чтобы у всех посылок есть трекинг номера
        without_tracking_number = queryset.filter(track__isnull=True)
        if without_tracking_number.exists():
            msg = 'Посылки без трекинг номеров: {}'.format(without_tracking_number.values_list('id', flat=True))
            self.message_user(request, msg, level=messages.WARNING)
            return

        new_delivery_act = DeliveryAct.objects.create()
        queryset.update(delivery_act=new_delivery_act)
        return HttpResponseRedirect(new_delivery_act.get_admin_change_url())

    to_act.short_description = 'Создать акт'


class ParselInline(admin.TabularInline):
    fields = ('id', 'order_id', 'track')
    readonly_fields = ('id', 'order_id', 'track')
    show_change_link = True
    model = Parsel
    extra = 0


@admin.register(DeliveryAct)
class DeliveryActAdmin(admin.ModelAdmin):
    list_display = ('id', 'act_id')
    inlines = (ParselInline,)
    actions = [send_to_boxberry]
    search_fields = ('id', 'act_id')
