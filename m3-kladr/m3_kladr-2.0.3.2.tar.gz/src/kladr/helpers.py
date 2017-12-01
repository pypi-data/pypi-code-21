#coding:utf-8

import models


def geo_rows_query(parent=None, filter=None):
    u"""
    Возвращает QuerySet для отбора записей из подсправочника KladrGeo
    """
    if parent == '-1':
        parent = None
    rows = models.KladrGeo.objects.filter(parent=parent)
    return rows


def geo_streets_query(parent, filter):
    u"""
    Возвращает QuerySet для отбора записей подсправочника KladrStreet
    """
    streets = models.KladrGeo.objects.get(pk=parent)
    return streets.kladrstreet_set.all()

