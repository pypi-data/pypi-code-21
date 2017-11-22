from functools import partial
from numpy import searchsorted

from zipline.utils.calendars import get_calendar
from zipline.data.bundles import register
from cn_zipline.bundles.tdx_bundle import tdx_bundle


def register_tdx(assets=None, minute=False, start=None, overwrite=False, end=None):
    if start:
        calendar = get_calendar('SHSZ')
        if not calendar.is_session(start):
            start = calendar.all_sessions[searchsorted(calendar.all_sessions,start)]
    register('tdx', partial(tdx_bundle, assets, minute, overwrite), 'SHSZ', start)