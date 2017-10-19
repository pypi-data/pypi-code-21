""" This module exists to allow overrides of calendars since they're so hard to get right
    programaticaly, and sometimes we need to correct a calendar very quickly.
    For now, I make no attempt to replicate a "fixed" version all the functionality in
    workalendar - but rather just create a new 'get holidays for a given year' function. """

from functools import lru_cache
from dateutil.parser import parse

from fincalendar.holiday_mapping import get_calendar
from fincalendar.holiday_overrides import OVERRIDES

def holidays_set(alpha_3_country_code, year, state_code=None):
    """ TODO - Add state_code handling """
    overrides = OVERRIDES.get(alpha_3_country_code) or {}
    calendar = get_calendar(alpha_3_country_code=alpha_3_country_code)
    holidays = calendar.holidays_set(year=year)
    holidays |= overrides.get("add", set())
    holidays -= overrides.get("subtract", set())
    return holidays
