"""
    ulmo.cpc.drought.core
    ~~~~~~~~~~~~~~~~~~~~~

    This module provides direct access to `Climate Predicition Center`_ `Weekly
    Drought Index`_ dataset.

    .. _Climate Prediction Center: http://www.cpc.ncep.noaa.gov/
    .. _Weekly Drought Index: http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought/
"""

import mando
try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter
from ulmo.cpc.drought.core import get_data

from tstoolbox import tsutils


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def cpc(state=None,
        climate_division=None,
        start_date=None,
        end_date=None):
    """
    This module provides direct access to `Climate Predicition Center`_ `Weekly
    Drought Index`_ dataset.

    .. _Climate Prediction Center: http://www.cpc.ncep.noaa.gov/
    .. _Weekly Drought Index: http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought/

    Parameters
    ----------
    state: ``None`` or str.
        If specified, results will be limited to the state corresponding to the
        given 2-character state code.
    climate_division: ``None`` or int.
        If specified, results will be limited to the climate division.
    {start_date}
    {end_date}
    """
    return tsutils.printiso(get_data(state=state,
                            climate_division=climate_division,
                            start=start_date,
                            end=end_date,
                            as_dataframe=True))


if __name__ == '__main__':
    r = cpc(state='FL',
            start_date='2017-01-01',
            end_date='2017-10-02')

    print('FL EVERYTHING')
    print(r)
