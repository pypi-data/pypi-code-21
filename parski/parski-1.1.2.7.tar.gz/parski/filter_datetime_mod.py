import re
import datetime

DASH_DATETIME_FORMAT = "%Y-%m-%d"
S8008S_DATETIME_FORMAT = "%Y/%m/%d"
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def filter_datetime(range_time, check_time):
    '''check string to see if it matches any datetime regex expression'''

    time_regex = {
        's8008s': re.compile('^\([0-9]{4}\/[0-9]{2}\/[0-9]{2}\)'),
        'iso': re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.{0,1}[0-9]{0,2}Z'),
        'slash_dash': re.compile('^[0-9]{4}\/[0-9]{2}\/[0-9]{2}'),
        'dash_slash': re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}')
    }

    def s8008s_conv(string):
        """convert s8008s format dates to datetimes"""
        return_dates = []
        dates = string.lstrip('(').rstrip(')').split(')(')
        for date in dates:
            return_dates.append(datetime.datetime.strptime(date, S8008S_DATETIME_FORMAT))
        return return_dates

    def iso_conv(string):
        """convert iso format dates to datetimes"""
        return_dates = []
        dates = string.split('/')
        for date in dates:
            date = date.split('.')[0].rstrip('Z') + 'Z'
            return_dates.append(datetime.datetime.strptime(date, ISO_DATETIME_FORMAT))
        return return_dates

    def slash_dash_conv(string):
        """convert slash_dash format dates to datetimes"""
        return_dates = []
        dates = string.split('-')
        for date in dates:
            return_dates.append(datetime.datetime.strptime(date, S8008S_DATETIME_FORMAT))
        return return_dates

    def dash_slash_conv(string):
        """convert dash_slash format dates to datetimes"""
        return_dates = []
        dates = string.split('/')
        for date in dates:
            return_dates.append(datetime.datetime.strptime(date, DASH_DATETIME_FORMAT))
        return return_dates

    date_conversion = {
        's8008s': s8008s_conv,
        'iso': iso_conv,
        'slash_dash': slash_dash_conv,
        'dash_slash': dash_slash_conv,
    }

    ##try to convert to date
    try:
        for key, value in time_regex.iteritems():
            if value.search(check_time):
                check_dates = date_conversion[key](check_time)
                if len(check_dates) != 1:
                    return False
                check_date = check_dates[0]
                break

        for key, value in time_regex.iteritems():
            if value.search(range_time):
                range_date = date_conversion[key](range_time)
                if len(range_date) == 1:
                    range_date.append(datetime.datetime(year=3000, month=12, day=31))
                break
        return bool(range_date[1]-check_date > datetime.timedelta(0) and check_date - range_date[0] > datetime.timedelta(0))
    except Exception as error:
        return False