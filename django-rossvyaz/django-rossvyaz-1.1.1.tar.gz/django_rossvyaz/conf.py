# coding: utf-8
from django.conf import settings

ROSSVYAZ_SOURCE_URLS = getattr(settings, 'ROSSVYAZ_SOURCE_URLS', {
    'def': 'https://www.rossvyaz.ru/docs/articles/Kody_DEF-9kh.csv',
})
ROSSVYAZ_CODING = getattr(settings, 'ROSSVYAZ_CODING', 'windows-1251')
ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS = getattr(settings, 'ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS', True)
