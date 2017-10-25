# coding: utf-8
import calendar
import datetime
from random import randrange


def rus_to_date(date_rus):
    """
        метод преобразует строку с датой в русском стандарте записи (ДД.ММ.ГГГГ) в питоний объект даты
    """
    if date_rus:
        try:
            return datetime.datetime.strptime(date_rus, '%d.%m.%Y').date()
        except Exception:
            return None
    else:
        return None


def rus_to_datetime(datetime_rus):
    """
        метод преобразует строку с датой и времнем в русском стандарте записи (ДД.ММ.ГГГГ ЧЧ:ММ:СС) в питоний объект даты
    """
    if datetime_rus:
        try:
            return datetime.datetime.strptime(datetime_rus, '%d.%m.%Y %H:%M:%S')
        except Exception:
            return None
    else:
        return None


def date_to_rus(date):
    """
        метод преобразует объект даты в строку даты в русском формате (ДД.ММ.ГГГГ)
    """
    if date:
        try:
            return date.strftime('%d.%m.%Y')
        except Exception:
            return date
    else:
        return ""


def datetime_to_rus(dt):
    """
        метод преобразует объект даты в строку даты в русском формате (ДД.ММ.ГГГГ ЧЧ:ММ)
    """
    if dt:
        try:
            return dt.strftime('%d.%m.%Y %H:%M')
        except Exception:
            return dt
    else:
        return ""


def iso_to_date(date_iso):
    """
        метод преобразует строку с датой в iso стандарте записи (ГГГГ-MM-ДД) в питоний объект даты
    """
    if date_iso:
        return datetime.datetime.strptime(date_iso[:10], '%Y-%m-%d').date()
    else:
        return None


def iso_to_datetime(datetime_iso):
    """
        метод преобразует строку с датой и временем в iso стандарте записи (ГГГГ-MM-ДД ЧЧ:ММ:СС) в питоний объект datetime
    """
    if datetime_iso:
        return datetime.datetime.strptime(datetime_iso, '%Y-%m-%d %H:%M:%S')
    else:
        return None


def date_to_datetime_lte(date):
    """
        Используем преобразование даты в дату-время для корректной фильтрации с помощью лукапа lte
    """
    if date:
        return datetime.datetime.combine(date, datetime.time(23, 59, 59))
    else:
        return None


def date_to_datetime(date):
    if date:
        return datetime.datetime(*(date.timetuple()[:6]))
    else:
        return None


def iso_date_to_rus(date_iso):
    """
        пробразует дату из ISO формата в русский
    """
    date = iso_to_date(date_iso)
    return date_to_rus(date)


def iso_datetime_to_rus(datetime_iso):
    """
        пробразует дату-время из ISO формата в русский
    """
    datetime_obj = iso_to_datetime(datetime_iso)
    return datetime_to_rus(datetime_obj)


def age_to_date(age):
    """
        преобразует возраст в год рождения. (Для фильтрации по дате рождения)
    """
    today = datetime.date.today()
    date = datetime.date(today.year - age - 1, today.month, today.day) + datetime.timedelta(days=1)
    return date


def date_to_timestamp(date):
    """
        date в unix timestamp в миллисекундах
    """
    date_tuple = date.timetuple()
    timestamp = calendar.timegm(date_tuple) * 1000
    return timestamp


def random_date(dt_from, dt_to):
    """
    This function will return a random datetime between two datetime objects.
    :param start: начальная дата
    :param end:
    """
    delta = dt_to - dt_from
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return dt_from + datetime.timedelta(seconds=random_second)


def is_date_ranges_intersection(t1start, t1end, t2start, t2end):
    """
     Проверяем совпадают ли периоды
    """
    return (t1start <= t2start <= t1end) or (t2start <= t1start <= t2end)
