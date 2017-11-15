# coding: utf-8
from __future__ import print_function, unicode_literals
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django_rossvyaz.conf import (
    ROSSVYAZ_SOURCE_URLS,
    ROSSVYAZ_CODING,
    ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS,
)
from django_rossvyaz.logic import clean_region, CleanRegionError
from django_rossvyaz.models import PhoneCode
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import Request, urlopen as urlopen_py3
    def urlopen(url):
        return urlopen_py3(Request(url))

DELETE_SQL = "DELETE FROM django_rossvyaz_phonecode WHERE phone_type='{}'"

INSERT_SQL = """
INSERT INTO django_rossvyaz_phonecode
(first_code, from_code, to_code, block_size, operator, region, phone_type)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

ERROR_SUBJECT = "Error of command rossvyaz_update"
send_message = ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS


avail_types = {item[0] for item in PhoneCode.PHONE_TYPE_CHOICES}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--phone-type', type=str)
        parser.add_argument('--clean-region', type=bool, default=False)
        parser.add_argument('--filename', type=str, default=None)
        parser.add_argument('--encoding', type=str, default=None)

    def handle(self, *args, **options):

        phone_type = options['phone_type']
        with_clean = options['clean_region']
        filename = options['filename']
        coding = options['encoding']

        if coding is None:
            coding = ROSSVYAZ_CODING

        if phone_type not in avail_types:
            _handle_error(
                'Bad phone_type={} (Avail only: {}. Add new '
                'type to django_rossvyaz.models.PhoneCode.PHONE_TYPE_CHOICES'
                ')'.format(repr(phone_type), repr(avail_types)))

        if filename is None:
            source_url = ROSSVYAZ_SOURCE_URLS[phone_type]
            print("Download csv-file: {}...".format(source_url))
            phonecodes_file = urlopen(source_url)
        else:
            print("Open csv-file: {}...".format(filename))
            phonecodes_file = open(filename, 'rb')
        phonecodes_file.readline()  # First line is titles row
        print("Start updating...")
        lines = _get_phonecode_lines(phonecodes_file, phone_type, coding, with_clean)
        phonecodes_file.close()
        cursor = connection.cursor()
        if hasattr(transaction, 'atomic'):
            # django >= 1.6
            try:
                with transaction.atomic():
                    _execute_sql(cursor, lines, phone_type)
            except Exception as e:
                _handle_error(e)
        else:
            # django < 1.6
            transaction.enter_transaction_management()
            try:
                transaction.managed(True)
                _execute_sql(cursor, lines, phone_type)
                transaction.commit()
            except Exception as e:
                _handle_error(e)
            finally:
                transaction.rollback()
                transaction.leave_transaction_management()
        return "Table rossvyaz phonecode is update.\n"

def _get_phonecode_lines(phonecode_file, phone_type, coding, with_clean):
    ret = []
    for l in phonecode_file:
        line = l.decode(coding).strip()
        if not line:
            continue
        rossvyaz_row = line.split(';')
        rossvyaz_row = [v.strip() for v in rossvyaz_row]
        region_name = rossvyaz_row[-1]

        if with_clean:
            try:
                rossvyaz_row[-1] = clean_region(region_name)
            except CleanRegionError as e:
                _handle_error(e)

        row = rossvyaz_row + [phone_type]
        ret.append(row)
    return ret

def _execute_sql(cursor, lines, phone_type):
    print("Delete old rows in table rossvyaz phonecodes...")
    cursor.execute(DELETE_SQL.format(phone_type))
    print("Write new data...")
    cursor.executemany(INSERT_SQL, [l for l in lines if l])

def _handle_error(e):
    message = "The data not updated: {}".format(traceback.format_exception(e))
    if send_message:
        mail_admins(subject=ERROR_SUBJECT, message=message)
    raise CommandError(message)
