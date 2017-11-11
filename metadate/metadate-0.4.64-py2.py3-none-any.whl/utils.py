import re
from enum import IntEnum

from dateutil.relativedelta import relativedelta


class Units(IntEnum):
    YEAR = 9
    SEASON = 8
    QUARTER = 7
    MONTH = 6
    WEEK = 5
    DAY = 4
    HOUR = 3
    MINUTE = 2
    SECOND = 1
    MICROSECOND = 0


RD_ARG_TO_UNIT = {
    "years": Units.YEAR,
    "year": Units.YEAR,
    "months": Units.MONTH,
    "month": Units.MONTH,
    "weeks": Units.WEEK,
    "week": Units.WEEK,
    "weekday": Units.DAY,
    "days": Units.DAY,
    "day": Units.DAY,
    "hours": Units.HOUR,
    "hour": Units.HOUR,
    "minutes": Units.MINUTE,
    "minute": Units.MINUTE,
    "seconds": Units.SECOND,
    "second": Units.SECOND,
    "microseconds": Units.MICROSECOND,
    "microsecond": Units.MICROSECOND,
}

freqs = ["yearly", "monthly", "weekly", "daily", "hourly", "minutely", "secondly"]
FREQ = {x: num for num, x in enumerate(freqs)}


def log(tag, x, verbose=False):
    if verbose:
        print("--- {} ------------".format(tag))
        print(x)


def add_tag(sentence, matches, color="mediumspringgreen"):
    # given textual matches between ranges like [(5, 10), (10, 15)]
    # this will clean up
    # first is 0,5
    news = ''
    lbound = 0
    hit = "<span style='background-color:{}'>{}</span>"
    for m in matches:
        news += sentence[lbound:m[0]]
        news += hit.format(color, sentence[m[0]:m[1]])
        lbound = m[1]
    news += sentence[matches[-1][1]:]
    return news


def strip_pm(txt, numbers_dict=None):
    txt = txt.lower()
    hoffset = 12 * ('pm' in txt or "afternoon" in txt or 'p.m' in txt)
    txt = txt.replace("afternoon", "")
    txt = txt.replace("'", " ")
    txt = re.sub(".?o.?clock", "", txt)
    if numbers_dict is None:
        parts = re.sub("[:hapm.]+", " ", txt).split()
    else:
        parts = re.sub(" ?[ap][.]?m[.]?$", " ", txt).split()
    parts = [x for x in parts if x]
    microsecond = None
    second = None
    minute = None
    if len(parts) == 4:
        hour, minute, second, microsecond = parts
    elif len(parts) == 3:
        hour, minute, second = parts
    elif len(parts) == 2:
        hour, minute = parts
    else:
        hour = parts[0]
    if numbers_dict is not None:
        hour = numbers_dict[hour]
    if int(hour) == 12 and hoffset:
        hoffset = 0
    hour = (hoffset + int(hour)) % 24
    hour = 0 if hour is None else int(hour)
    minute = 0 if minute is None else int(minute)
    second = 0 if second is None else int(second)
    microsecond = 0 if microsecond is None else int(microsecond)
    return hour, minute, second, microsecond


def erase_level(d, level):
    if level == Units.YEAR:
        d = d.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.SEASON:
        d = d.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.QUARTER:
        d = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.MONTH:
        d = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.WEEK:
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.DAY:
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    elif level == Units.HOUR:
        d = d.replace(minute=0, second=0, microsecond=0)
    elif level == Units.MINUTE:
        d = d.replace(second=0, microsecond=0)
    elif level == Units.SECOND:
        d = d.replace(microsecond=0)
    return d


def resolve_end_period(start_date, level, past_boundary, now):
    date_changed = False
    start_date = erase_level(start_date, level)
    if level == Units.YEAR:  # year
        end_date = start_date + relativedelta(years=1)
    elif level == Units.SEASON:  # season
        end_date = start_date + relativedelta(months=3)
    elif level == Units.QUARTER:  # quarter
        for cap in [1, 4, 7, 10]:
            if start_date.month <= cap:
                break
        end_month = (cap + 3)
        if end_month > 12:
            end_date = start_date + relativedelta(month=end_month % 12, day=1, years=1)
        else:
            end_date = start_date + relativedelta(month=end_month, day=1)
    elif level == Units.MONTH:
        end_date = start_date + relativedelta(months=1)
    elif level == Units.WEEK:
        end_date = start_date + relativedelta(days=7)
    elif level == Units.DAY:
        end_date = start_date + relativedelta(days=1)
    elif level == Units.HOUR:
        end_date = start_date + relativedelta(hours=1)
    elif level == Units.MINUTE:
        end_date = start_date + relativedelta(minutes=1)
    elif level == Units.SECOND:
        end_date = start_date + relativedelta(seconds=1)
    elif level == Units.MICROSECOND:
        end_date = start_date + relativedelta(microseconds=1)
    # has to be tighter
    # if end_date < past_boundary:
    #     start_date = start_date.replace(year=start_date.year + 1)
    #     end_date = end_date.replace(year=end_date.year + 1)
    #     date_changed = True
    # elif start_date < past_boundary:
    #     start_date = now
    #     date_changed = True
    return start_date, end_date, date_changed


BOUNDARIES = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}
