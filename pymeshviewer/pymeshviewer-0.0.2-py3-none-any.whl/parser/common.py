from datetime import datetime


def parse_datetime(datetime_string: str) -> datetime:
    """
    Parses the datetime string from meshviewer json and returns it as a datetime object
    :param datetime_string: datetime string from yanic json
    :return: parsed datetime string as datetime object
    """
    return datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S%z')