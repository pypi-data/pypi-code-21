#coding:utf-8
from django.db.models.query_utils import Q
from django.conf import settings

from m3 import M3JSONEncoder
from m3.actions import (
    Action, PreJsonResult, OperationResult, ActionPack, ActionController)
from m3.actions.tree_packs import BaseTreeDictionaryModelActions

from models import KladrGeo, KladrStreet
from ui import KLADRGeoEditWindow, KLADRStreetEditWindow


kladr_controller = ActionController(url='/m3-kladr')
if hasattr(settings, 'ROOT_URL'):
    kladr_controller.url = settings.ROOT_URL + kladr_controller.url


class Kladr_DictPack(BaseTreeDictionaryModelActions):
    u"""
    Пак для справочника КЛАДР
    """
    url = '/kladr'
    # Включаем проверку прав пользователя.
    need_check_permission = True

    title = u'Классификатор адресов России (КЛАДР)'
    verbose_name = u'Классификатор адресов России (КЛАДР)'
    tree_model = KladrGeo
    list_model = KladrStreet

    list_columns = [('socr', u'Сокращение', 20),
                    ('name', u'Улица')]
    tree_columns = [('name', u'Геогр. пункт', 240),
                    ('socr', u'Сокращение', 90),
                    ('zipcode', u'Индекс', 60)]

    filter_fields = ['code', 'name']
    tree_filter_fields = ['name', 'zipcode']

    width, height = 910, 600
    tree_width = 390

    edit_window = KLADRStreetEditWindow
    edit_node_window = KLADRGeoEditWindow


class KLADRPack(ActionPack):
    u"""
    Пак действий с КЛАДРом
    """
    url = ''

    def __init__(self):
        super(KLADRPack, self).__init__()
        self.get_places_action = KLADRRowsAction()
        self.get_streets_action = StreetRowsAction()
        self.get_addr_action = KLADRGetAddrAction()
        self.actions = [
            self.get_places_action,
            self.get_streets_action,
            self.get_addr_action
        ]

    @classmethod
    def get_place_name(cls, code):
        u"""
        Возвращает имя географического объекта (субъекта, населенного пункта)
        в строковом виде по коду
        """
        place = KladrGeo.objects.select_related(
            'parent', 'parent__parent', 'parent__parent__parent'
        ).filter(
            code=code
        )
        return place[0].display_name() if place else ''

    @classmethod
    def get_place(cls, code):
        u"""
        Возвращает географический объект в JSON-формате по коду
        """
        place = KladrGeo.objects.select_related(
            'parent', 'parent__parent', 'parent__parent__parent'
        ).filter(
            code=code
        )
        return M3JSONEncoder().encode(place[0]) if place else None

    @classmethod
    def get_street_name(cls, code):
        u"""
        Возвращает полный адрес в строковом виде по коду
        """
        street = KladrStreet.objects.select_related('parent').filter(code=code)
        return street[0].display_name() if street else ''

    @classmethod
    def get_street(cls, code):
        u"""
        Возвращает объект улицы в JSON-формате по коду
        """
        street = KladrStreet.objects.select_related('parent').filter(code=code)
        return M3JSONEncoder().encode(street[0]) if street else None


class KLADRRowsAction(Action):
    u"""
    Экшен, возвращающий строки с географическими объектами
    """
    url = '/kladr_rows$'
    MAX_DEPTH = 3  # макс. глубина вложенности детей в родителя

    def run(self, request, context):
        filter = request.REQUEST.get('filter')
        if filter:  # бывают случаи, когда фильтр приходит пустой
            fields = ['name', 'code', 'socr']
            words = filter.strip().split(' ')
            # первым этапом найдем территории подходящие под фильтр в имени
            condition = Q()
            for word in words:
                field_condition = Q()
                for field_name in fields:
                    field_condition |= Q(**{field_name + '__icontains': word})

                condition &= field_condition

            places = KladrGeo.objects.filter(condition).select_related(
                'parent', 'parent__parent', 'parent__parent__parent'
            ).order_by(
                'level', 'name'
            )[0:50]
            # если не нашли, то будем искать с учетом родителей
            if len(places) == 0:
                condition = Q()
                for word in words:
                    field_condition = Q()
                    for field_name in fields:
                        for depth in range(self.MAX_DEPTH + 1):
                            field_condition |= Q(**{
                                '{}{}__icontains'.format(
                                    'parent__' * depth,
                                    field_name
                                ): word
                            })

                    condition &= field_condition

                places = KladrGeo.objects.filter(condition).select_related(
                    'parent', 'parent__parent', 'parent__parent__parent'
                ).order_by(
                    'level', 'name'
                )[0:50]
        else:
            places = []
        result = {'rows': list(places), 'total': len(places)}
        return PreJsonResult(result)


class StreetRowsAction(Action):
    u"""
    Экшен, возвращающий строки с улицами
    """
    url = '/street_rows$'

    MAX_DEPTH = 3  # макс. глубина вложенности детей в родителя

    def run(self, request, context):
        filt = request.REQUEST.get('filter')
        if filt:  # бывают случаи, когда фильтр приходит пустой
            place_code = request.REQUEST.get('place_code')
            place_filter = Q()
            if place_code:
                try:
                    place_id = KladrGeo.objects.get(code=place_code)
                except (
                    KladrGeo.DoesNotExist,
                    KladrGeo.MultipleObjectsReturned
                ):
                    pass
                else:
                    for depth in range(self.MAX_DEPTH):
                        place_filter |= Q(**{
                            '%sparent' % ('parent__' * depth): place_id
                        })

            fields = ['name', 'code', 'socr']
            words = filt.strip().split()

            # формирователь выборки улиц
            def query_streets(condition):
                return KladrStreet.objects.filter(
                    condition,
                    place_filter,
                ).select_related(
                    'parent'
                ).order_by(
                    'name'
                )[0:50]

            # первым этапом найдем территории подходящие под фильтр в имени
            condition = Q()
            for word in words:
                field_condition = Q()
                for field_name in fields:
                    field_condition |= Q(**{field_name + '__icontains': word})
                condition &= field_condition
            places = query_streets(condition)

            # если не нашли, то будем искать с учетом родителей
            if not places.exists():
                condition = Q()
                for word in words:
                    field_condition = Q()
                    for field_name in fields:
                        for depth in range(self.MAX_DEPTH + 1):
                            field_condition |= Q(**{
                                '{0}{1}__icontains'.format(
                                    'parent__' * depth,
                                    field_name
                                ): word
                            })
                    condition &= field_condition
                places = query_streets(condition)
        else:
            places = []
        result = {'rows': list(places), 'total': len(places)}
        return PreJsonResult(result)


def GetAddr(place, street=None, house=None, flat=None, zipcode=None, corps=None):
    u"""
    Формирует строку полного адреса по выбранным значениям КЛАДРа

    :param place: населенный пункт
    :param street: улица
    :param house: дом
    :param flat: квартира
    :param zipcode: индекс
    :param corps: корпус
    :return:
    """
    if not place:  # бывают случаи, когда территория приходит пустой
        return ''
    # Получаем населенный пункт
    if isinstance(place, (str, unicode)):
        qs = KladrGeo.objects.filter(code=place)
        if qs.count() > 0:
            place = qs.get()
        else:
            return ''
    elif not isinstance(place, KladrGeo):
        raise TypeError()

    # Получаем улицу
    if isinstance(street, (str, unicode)):
        qs = KladrStreet.objects.filter(code=street)
        if qs.count() > 0:
            street = qs.get()
        else:
            street = None
    elif street and not isinstance(street, KladrStreet):
        raise TypeError()

    u"""
    типАдреса = 0 или 1
    текИндекс = 0
    адрес = ""
    текУровень = 5
    текЭлемент = кодУлицы
    если типАдреса = 0
        раделитель = ", "
    иначе
        раделитель = ","
    пока текЭлемент >= 0
        если типАдреса > 0 и текЭлемент = 0
            выход
        для всех территорий у которых код = текЭлемент
            имя = территория.имя
            родитель = территория.родитель
            уровень = территория.уровень
            индекс = территория.индекс
            сокр = территория.сокр
            если текИндекс = 0 и индекс <> 0, то текИндекс = индекс
            если типАдреса = 0
                адрес = сокр+" "+имя+раделитель+адрес
            иначе
                текЭлемент = родитель
                пока текУровень > уровень
                    текУровень = текУровень-1
                    адрес = раделитель+адрес
                адрес = сокр+" "+имя+раделитель+адрес
                текУровень = текУровень-1
        если текЭлемент = 0 и родитель = 0
            выход
        текЭлемент = родитель
    если типАдреса = 0
        если индекс > 0
            адрес = индекс+раделитель+адрес
    иначе
        пока текУровень > 1
            текУровень = текУровень-1
            адрес = раделитель+адрес
        адрес = регион+раделитель+адрес
        если индекс > 0
            адрес = раделитель+индекс+раделитель+адрес
        иначе
            адрес = раделитель+раделитель+адрес
    """
    addr_type = 0
    curr_index = zipcode or ''
    addr_text = ''
    curr_level = 5
    if street:
        curr_item = street
    else:
        curr_item = place
    if addr_type == 0:
        delim = ', '
    else:
        delim = ','
    while curr_item:
        if addr_type != 0 and not curr_item.parent:
            break
        if curr_index == '' and curr_item.zipcode:
            curr_index = curr_item.zipcode
        if addr_type == 0:
            addr_text = ''.join((
                curr_item.socr, " ", curr_item.name, delim, addr_text))
        else:
            if curr_item == street:
                lv = 4
            else:
                lv = curr_item.level
            while curr_level > lv:
                curr_level -= 1
                addr_text = ''.join((delim, addr_text))
            addr_text = ''.join((
                curr_item.socr, " ", curr_item.namebind_pack, delim, addr_text
            ))
            curr_level -= 1
        curr_item = curr_item.parent
    if addr_type == 0:
        if curr_index != '':
            addr_text = ''.join((curr_index, delim, addr_text))
    else:
        while curr_level > 1:
            curr_level -= 1
            addr_text = delim + addr_text
        addr_text = ''.join((u'регион', delim, addr_text))
        if curr_index != '':
            addr_text = ''.join((curr_index, delim, addr_text))
        else:
            addr_text = ''.join((delim, delim, addr_text))
    # если нет дома и корпуса и квартиры, то уберем последний разделитель
    if not (house or corps or flat):
        addr_text = addr_text.rstrip(delim)
    else:
        if house:
            addr_text = ''.join((addr_text, u'д. ', house))
        if corps:
            addr_text = u'{}{}корп. {}'.format(addr_text, delim, corps)
        if flat:
            addr_text = ''.join((addr_text, delim, u'кв. ', flat))
    return addr_text


class KLADRGetAddrAction(Action):
    u"""
    Расчет адреса по составляющим
    """
    url = '/kladr_getaddr$'

    def run(self, request, context):
        place = request.REQUEST.get('place')
        street = request.REQUEST.get('street')
        house = request.REQUEST.get('house')
        flat = request.REQUEST.get('flat')
        zipcode = request.REQUEST.get('zipcode')
        addr_cmp = request.REQUEST.get('addr_cmp', '')
        addr_text = GetAddr(place, street, house, flat, zipcode)
        result = u'''(function () {{
            Ext.getCmp("{0}").setValue("{1}");
        }})()
        '''.format(addr_cmp, addr_text or '')
        return OperationResult(success=True, code=result)
