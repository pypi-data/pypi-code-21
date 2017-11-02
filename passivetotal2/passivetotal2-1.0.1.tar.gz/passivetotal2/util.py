from datetime import datetime


def parse_datetime(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
