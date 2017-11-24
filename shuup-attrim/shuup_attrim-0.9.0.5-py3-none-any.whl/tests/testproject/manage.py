#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line


if __name__ == '__main__':
    if 'test' in sys.argv:
        os.environ.setdefault('IS_SHUUP_TEST', '1')
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'attrim.tests.testproject.settings',
    )
    execute_from_command_line(sys.argv)
