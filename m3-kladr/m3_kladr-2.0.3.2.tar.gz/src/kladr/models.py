#coding:utf-8

from django.db import models

from m3 import json_encode


class KladrGeo(models.Model):
    u"""
    Модель справочника КЛАДРа
    """
    parent = models.ForeignKey('KladrGeo', null=True, blank=True)
    name = models.CharField(max_length=40, db_index=True)
    socr = models.CharField(max_length=10, db_index=True)
    code = models.CharField(max_length=13, db_index=True)
    zipcode = models.CharField(max_length=6)
    gni = models.CharField(max_length=4)
    uno = models.CharField(max_length=4)
    okato = models.CharField(max_length=11)
    status = models.CharField(max_length=1)
    level = models.IntegerField(null=True, blank=True)
    
    @json_encode
    def display_name(self):
        if self.parent:
            return ''.join((
                self.socr, " ", self.name, " / ", self.parent.display_name()))
        else:
            return ' '.join((self.socr, self.name))

    @json_encode
    def addr_name(self):
        u"""
        Возвращает наименование в формате текстового адреса
        """
        curr = self
        res = None
        while curr:
            if res:
                res = ''.join((curr.socr, " ", curr.name, ", ", res))
            else:
                res = ' '.join((curr.socr, curr.name))
            curr = curr.parent
        return res


class KladrStreet(models.Model):
    u"""
    Модель справочника улиц КЛАДР
    """ 
    parent = models.ForeignKey('KladrGeo', null=True, blank=True)
    name = models.CharField(max_length=40, db_index=True)
    socr = models.CharField(max_length=10, db_index=True)
    code = models.CharField(max_length=17, db_index=True)
    zipcode = models.CharField(max_length=6)
    gni = models.CharField(max_length=4)
    uno = models.CharField(max_length=4)
    okato = models.CharField(max_length=11)
    
    @json_encode
    def display_name(self):
        if self.parent:
            return ''.join((self.socr, " ", self.name, " / ", self.parent.name))
        else:
            return ' '.join((self.socr, self.name))
