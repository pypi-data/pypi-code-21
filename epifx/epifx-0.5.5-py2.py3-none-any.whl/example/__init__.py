"""Example of local forecast settings."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import datetime
import errno
import io
import logging
import numpy as np
import os.path
import pkgutil
import pypfilt.summary

from ..obs import datetime_conv


def copy(dest_dir='.'):
    """
    Copy the example local forecast settings to a directory.

    :param dest_dir: The destination directory.
    """
    logger = logging.getLogger(__name__)
    logger.info('destination directory: {}'.format(dest_dir))

    def copy_to(src_files, out_dir, prefix=""):
        # Create the destination directory (and missing parents) as needed.
        if not os.path.isdir(out_dir):
            # Create with mode -rwxr-x---.
            try:
                logger.info('creating {}'.format(out_dir))
                os.makedirs(out_dir, mode=0o750)
            except OSError as e:
                # Potential race condition with multiple script instances.
                if e.errno != errno.EEXIST:
                    logger.warning('could not create {}'.format(out_dir))
                    logger.warning(e)
                    return

        copy_files = []
        for src_file in src_files:
            dest_file = os.path.join(out_dir, src_file)
            if os.path.isfile(dest_file):
                logger.info('{} exists, skipping'.format(dest_file))
            else:
                copy_files.append((src_file, dest_file))

        for (src, dest) in copy_files:
            logger.info('writing {}'.format(dest))
            with open(dest, 'wb') as f:
                f.write(pkgutil.get_data(__name__, prefix + src))

    www_files = ['index.html', 'plot.js', 'style.css']
    example_files = ['epifxlocns.py', 'google-flu-trends-aus.ssv']

    copy_to(example_files, dest_dir)
    copy_to(www_files, os.path.join(dest_dir, 'www'), prefix="www/")


def gft_obs(year, obs_unit, col):
    """
    Return Australian Google Flu Trends data as a list of observations.

    :param year: The calendar year (2006-2014).
    :param obs_unit: The observation unit to apply to each observation.
    :param col: The data column, must be one of: ``'AUS', 'ACT', 'NSW', 'QLD',
        'SA', 'VIC' 'WA'``.
    :raises ValueError: if ``year`` or ``col`` are invalid.
    """
    col_map = {
        'AUS': 2, 'ACT': 3, 'NSW': 4, 'QLD': 5, 'SA': 6, 'VIC': 7, 'WA': 8,
    }
    if col not in col_map:
        raise ValueError("invalid GFT data column: {}".format(col))
    col_types = pypfilt.summary.dtype_names_to_str([
        ('year', np.int32), ('date', datetime.datetime), ('count', np.int32)
    ])
    col_convs = {1: lambda s: datetime_conv(s)}
    col_read = [0, 1, col_map[col]]

    gft_file = 'google-flu-trends-aus.ssv'
    gft_data = pkgutil.get_data(__name__, gft_file)
    f = io.StringIO(gft_data.decode('ascii'))
    df = np.loadtxt(f, skiprows=1, dtype=col_types, converters=col_convs,
                    usecols=col_read)

    mask = df['year'] == year
    if not np.any(mask):
        raise ValueError("invalid GFT year: {}".format(year))

    df = df[mask]
    nrows = df.shape[0]

    return [{'date': df['date'][i],
             'value': df['count'][i],
             'unit': obs_unit,
             'period': 7,
             'source': gft_file}
            for i in range(nrows)]
