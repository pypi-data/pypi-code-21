# -*- coding: utf8 -*-

"""
Constants per utilitzar a utils.
"""

import os
import sys


IS_PYTHON_3 = sys.version_info[0] == 3
TMP_FOLDER = os.environ.get('TMP_FOLDER', '/tmp')
APP_CHARSET = os.environ.get('APP_CHARSET', 'utf8')

if APP_CHARSET == 'utf8':
    MARIA_CHARSET = 'utf8mb4'
    MARIA_COLLATE = 'utf8mb4_bin'
    os.environ['NLS_LANG'] = '.UTF8'
elif APP_CHARSET == 'latin1':
    MARIA_CHARSET = 'latin1'
    MARIA_COLLATE = 'latin1_general_ci'
    os.environ['NLS_LANG'] = '.WE8ISO8859P1'
else:
    raise AttributeError('APP_CHARSET {} not supported'.format(APP_CHARSET))

MARIA_STORAGE = 'MyISAM'
os.environ['NLS_DATE_FORMAT'] = 'YYYYMMDD'
