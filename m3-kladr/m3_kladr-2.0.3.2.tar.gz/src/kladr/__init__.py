#coding:utf-8
"""
Приложение для работы с КЛАДР
"""

from fill_kladr import fill_kladr

def import_kladr(region_only=None, dbf_path=''):
    u"""
    Импортирует кладр из папки dbf_path. Если не задавать dbf_path,
    то система возьмет путь m3/externals.
    
    В случае если необходимо загрузить данные только по одному региону,
    то необходимо в region передать строку с двумя символами региона.
    Например, region_only = '16'
    """
    fill_kladr(region_only, dbf_path)
