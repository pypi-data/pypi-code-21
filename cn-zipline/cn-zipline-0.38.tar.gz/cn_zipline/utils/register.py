from functools import partial
from numpy import searchsorted
import pandas as pd

from zipline.utils.calendars import get_calendar
from zipline.data.bundles import register
from cn_zipline.bundles.tdx_bundle import tdx_bundle


def register_tdx(assets=None, minute=False, start=None, overwrite=False, end=None):
    calendar = get_calendar('SHSZ')
    if not end:
        now = pd.to_datetime('now')
        if now.time() < pd.to_datetime('15:30').tz_localize('Asia/Shanghai').tz_convert("UTC").time():
            end = now.date() - pd.Timedelta('24 H')
            end = calendar.all_sessions[calendar.all_sessions.get_loc(end,method='ffill')]
        else:
            end = now.date()
    if start:
        if not calendar.is_session(start):
            start = calendar.all_sessions[searchsorted(calendar.all_sessions, start)]
    register('tdx', partial(tdx_bundle, assets, minute, overwrite), 'SHSZ', start,end)
