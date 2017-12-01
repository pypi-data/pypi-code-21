#coding:utf-8
from m3_ext.gears.edit_windows import GearEditWindow
from m3_ext.ui.fields.simple import ExtHiddenField, ExtStringField


# Копипаста из МТР
class DictSimpleEditWindow(GearEditWindow):
    u""" 
    Базовое окно для всех справочников 
    """
    def __init__(self, create_new=True, *args, **kwargs):
        super(DictSimpleEditWindow, self).__init__(*args, **kwargs)
        self.frozen_size(430, 123)
        self.modal = True
        self.create_new = create_new
        
        # Стандартные поля
        self.field_hidden = ExtHiddenField(name='id')
        self.field_code = ExtStringField(
            width=10, label=u'Код', name='code', 
            anchor='60%', allow_blank=True)
        self.field_name = ExtStringField(
            width=200, label=u'Наименование',
            name='name', anchor='100%', allow_blank=False)
        
        self.form.items.extend([
            self.field_hidden,           
            self.field_code,
            self.field_name
        ])
        
    def configure_for_dictpack(self, **k):
        if self.create_new:
            self.title = u'Создание новой записи: ' + k['pack'].title
        else:
            self.title = u'Редактирование записи: ' + k['pack'].title


class KLADRStreetEditWindow(DictSimpleEditWindow):
    u"""
    Форма редактирования улиц КЛАДР
    """
    def __init__(self, *args, **kwargs):
        super(KLADRStreetEditWindow, self).__init__(*args, **kwargs)
        self.frozen_size(430, 280)
        
        self.field_name.label = u'Улица'
        self.field_code.width = 300
        self.form.items.extend([
            ExtStringField(width=300, label=u'Сокращение', name='socr'),
            ExtStringField(width=300, label=u'Индекс', name='zipcode'),
            ExtStringField(width=300, label=u'Код ИФНС', name='gni'),
            ExtStringField(width=300, label=u'Код тер.уч. ИФНС', name='uno'),
            ExtStringField(width=300, label=u'Код ОКАТО', name='okato'),
        ])
        # Скрытое поля для группы
        self.form.items.append(ExtHiddenField(name='parent_id'))
        

class KLADRGeoEditWindow(DictSimpleEditWindow):
    u"""
    Форма редактирования географических объектов КЛАДР
    """
    def __init__(self, *args, **kwargs):
        super(KLADRGeoEditWindow, self).__init__(*args, **kwargs)
        self.frozen_size(430, 320)
        
        self.field_name.label = u'Геогр.пункт'
        self.field_code.width = 300
        self.form.items.extend([
            ExtStringField(width=300, label=u'Сокращение', name='socr'),
            ExtStringField(width=300, label=u'Индекс', name='zipcode'),
            ExtStringField(width=300, label=u'Код ИФНС', name='gni'),
            ExtStringField(width=300, label=u'Код тер.уч. ИФНС', name='uno'),
            ExtStringField(width=300, label=u'Код ОКАТО', name='okato'),
            ExtStringField(width=300, label=u'Статус', name='status')
        ])
        # Скрытое поле для родительской группы
        self.form.items.append(ExtHiddenField(name='parent_id'))
