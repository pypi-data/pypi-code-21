# coding=utf-8
from datetime import datetime


SERVER_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'  # ISO 8601 format
DISPLAY_DATETIME_FORMAT = '%b %d, %H:%M'


def format_datetime(server_datetime):
    d = datetime.strptime(server_datetime, SERVER_DATETIME_FORMAT)
    return datetime.strftime(d, DISPLAY_DATETIME_FORMAT)


SHORT_TEXT_MAX_LENGTH = 20
LONG_TEXT_MAX_LENGTH = 50


def create_text_truncator(max_length):
    def truncate_text(text):
        if max_length <= 0:
            return text

        text = ' '.join(text.splitlines())

        if len(text) > max_length:
            text = text[:max_length] + '...'

        return text

    return truncate_text


truncate_short_text = create_text_truncator(SHORT_TEXT_MAX_LENGTH)
truncate_long_text = create_text_truncator(LONG_TEXT_MAX_LENGTH)
