# -*- coding: utf-8 -*-
from bgionline.utils import *
from bgionline.utils.config import *


def test_try_call():
    assert try_call(to_zhcn, 'qwe') is None


def test_get_fully_path():
    bgionline.config.current_wd = '/'
    bgionline.config.save()
    assert get_fully_path('/', is_end=False) is '/'
    assert get_fully_path('/') is '/'
    assert get_fully_path('/a', is_end=False) == '/a'
    assert get_fully_path('/a') == '/a/'
    assert get_fully_path('a') == '/a/'
    assert get_fully_path('a', is_end=False) == '/a'

    bgionline.config.current_wd = '/a/'
    bgionline.config.save()
    assert get_fully_path('a') == '/a/a/'
    assert get_fully_path('a', False) == '/a/a'
    assert get_fully_path('') == '/a/'
    assert get_fully_path('', False) == '/a'
    assert get_fully_path('/', is_end=False) is '/'
    assert get_fully_path('/') is '/'


def test_to_zhcn():
    assert to_zhcn('a') == 'a'


def test_get_sts_token():
    assert get_sts_token() == get_sts_token()


def test_parse_size():
    assert parse_size(1024) == '  1.0  KB'


def test_parse_time():
    assert parse_time(3620) == '   1:00:20'
