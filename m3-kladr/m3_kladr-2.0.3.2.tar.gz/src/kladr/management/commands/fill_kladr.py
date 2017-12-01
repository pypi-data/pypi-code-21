#coding:utf-8
'''
Created on 17.05.2011
@author: Сафиуллин В. А.
'''
from optparse import make_option

from django.core.management.base import BaseCommand

from kladr.fill_kladr import fill_kladr


class Command(BaseCommand):
    help = (
        u'Загрузка/обновление КЛАДРа из dbf-файлов KLADR.dbf и STREET.dbf\n'
        u'Последнюю версию качать отсюда - '
        u'http://www.gnivc.ru/Document.aspx?id=1571\n'
        u'Если путь к dbf-файлам не задан, то используется текущая папка.\n'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--dbf_path', type='string',
            help=u'Путь к dbf-файлам'),

        make_option(
            '--noclear', action='store_true',
            help=u'Отключает удаление старого КЛАДРа перед загрузкой'),

        make_option(
            '--force', action='store_true',
            help=u'Не задает вопросов'),

        make_option(
            '--update', action='store_true',
            help=u'Обновляет существующие записи вместо создания новых'),
    )

    def handle(self, *args, **options):
        flag_clear = not bool(options.get('noclear', False))
        flag_force = bool(options.get('force', False))
        flag_update = bool(options.get('update', False))
        dbf_path = options.get('dbf_path')

        if not flag_force:
            print u'Вы действительно хотите обновить КЛАДР?'
            answer = raw_input('[y/n] ')
            if answer.lower() != 'y':
                return

        fill_kladr(
            dbf_path=dbf_path,
            clear_before=flag_clear,
            update=flag_update,
        )
