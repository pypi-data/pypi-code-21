from datetime import date, datetime

DATE_FORMAT = "%d-%m-%Y"
DATE_TIME_FORMAT = DATE_FORMAT + "-%H:%M:%S"


def today():
    return str(date.today())


def today_date():
    return datetime.today().strftime(DATE_FORMAT)


def today_datetime():
    return datetime.today().strftime(DATE_TIME_FORMAT)
