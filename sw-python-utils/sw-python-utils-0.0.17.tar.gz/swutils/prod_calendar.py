# coding: utf-8
"""
Производственный календарь.
"""
import json
import os
import datetime
import requests

WORKING_TYPE_WORK = 0
WORKING_TYPE_HOLIDAY = 2
WORKING_TYPE_SHORT = 3

DEFAULT_CACHE_PATH = '/tmp/basicdata_calend.json'


def is_working_time(date_time, use_cache=False, cache_path=DEFAULT_CACHE_PATH):
    exceptions = _get_prod_exceptions(use_cache=use_cache, cache_path=cache_path)

    work_first_hour = 10
    work_last_hour = 17
    is_work_day = date_time.weekday() < 5

    year = str(date_time.year)
    month = str(date_time.month)
    day = str(date_time.day)
    if exceptions.get(year) and exceptions[year].get(month) and exceptions[year][month].get(day):
        working_type = exceptions[year][month][day]['isWorking']

        if working_type == WORKING_TYPE_HOLIDAY:
            is_work_day = False

        elif working_type == WORKING_TYPE_SHORT:
            work_last_hour = 16

        elif working_type == WORKING_TYPE_WORK:
            is_work_day = True

    is_work_time = work_first_hour <= date_time.hour <= work_last_hour

    return is_work_day and is_work_time


def _get_prod_exceptions(use_cache=False, cache_path=DEFAULT_CACHE_PATH):
    if not use_cache:
        return _load_prod_exceptions()

    if _is_cache_available(cache_path=cache_path):
        exceptions = _load_cache(cache_path)
    else:
        exceptions = _load_prod_exceptions()
        _save_cache(exceptions, cache_path)

    return exceptions


def _load_prod_exceptions():
    """
    Используется http://basicdata.ru/api/calend/
    Как написано на сайте:
    Предполагается, что дни недели с понедельника по пятницу включительно являются рабочими,
    а суббота и воскресение — выходными.
    Данное API возвращает все исключения из этого правила
    """
    url = 'http://basicdata.ru/api/json/calend/'
    exceptions = requests.get(url).json()
    return exceptions['data']


def _save_cache(data, cache_path):
    with open(cache_path, 'w') as cache_file:
        json.dump(data, cache_file)


def _load_cache(cache_path):
    with open(cache_path) as cache_file:
        return json.load(cache_file)


def _is_cache_available(cache_path, expiration_days=1):
    if not os.path.isfile(cache_path):
        return False

    now = datetime.datetime.now()
    cache_modify_dt = datetime.datetime.fromtimestamp(os.path.getmtime(cache_path))
    delta = now - cache_modify_dt
    if delta.days >= expiration_days:
        return False

    try:
        with open(cache_path) as cache_file:
            json.load(cache_file)
    except Exception:
        return False

    return True
