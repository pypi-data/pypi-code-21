####
# bomail.util.datestr
#
# Utilities for parsing "date strings"
# which can either be absolute (2050-03-25)
# or relative (p4.5y meaning plus 4.5 years from now)
####

import datetime
import dateutil.parser
from dateutil import tz
from dateutil.relativedelta import relativedelta

datestr_str = """
'date strings' are used in search and scheduling, e.g.
    bomail search -a datestr   # search after given date
    bomail chstate -s datestr  # schedule for given date

datestr can be in:
 (1) Absolute format: yyyy-mm-ddTHH:MM
     or any prefix of this.

 (2) Relative format: p[num][unit]
     meaning plus num of units from now.
     Unit can be y (year), w (week), H (hour), M (minute).
     month is not allowed, to avoid confusing with minute.
     If num has a decimal point, adds the exact amount.
     Else, rounds down to the nearest unit.

 (3) Relative format:  m[num][unit]
     meaning minus num of units before now.
     Same details as (2) apply.

Some examples for absolute date:
  2050              # Jan 1st, 2050 at 00:00
  2050-03-07        # Mar 7th, 2050 at 00:00
  2050-03-07T11     # Mar 7th, 2050 at 11:00

Some examples for relative date:
  p1d               # tomorrow at 00:00, no matter what time it is today
  p1.d              # tomorrow at the same time of day that it is right now
  p1.5d             # 36 hours from now
  m3w               # 3 weeks before now, rounded down to Monday at 00:00
  m3.5w             # exactly 3.5 weeks before now (to the minute)
"""


# convert schedule string to datetime object
def get_datetime(schedstr):
  if schedstr[0] == "p":
    mult = 1.0  # forward in time
  elif schedstr[0] == "m":
    mult = -1.0
  else:
    # absolute
    try:
      return dateutil.parser.parse(schedstr, default=datetime.datetime(1,1,1))
    except:
      return None
  # else: relative
  local_tz = tz.tzlocal()
  now = datetime.datetime.now(local_tz)
  numstr = schedstr[1:-1]
  num = mult*float(numstr)  # forward or back in time
  isfloat = "." in numstr

  result = None
  suffix = schedstr[-1]
  if suffix == "y":
    result = now + relativedelta(years=num)
    if not isfloat:
      result = datetime.datetime(year=result.year)
  elif suffix == "w":
    result = now + relativedelta(weeks=num)
    if not isfloat:
      dayoffset = relativedelta(days=result.weekday())
      result = datetime.datetime(year=result.year, month=result.month, day=result.day) - dayoffset
  elif suffix == "d":
    result = now + relativedelta(days=num)
    if not isfloat:
      result = datetime.datetime(year=result.year, month=result.month, day=result.day)
  elif suffix == "H":
    result = now + relativedelta(hours=num)
    if not isfloat:
      result = datetime.datetime(year=result.year, month=result.month, day=result.day, hour=result.hour)
  elif suffix == "M":
    result = now + relativedelta(minutes=num)
    if not isfloat:
      result = datetime.datetime(year=result.year, month=result.month, day=result.day, hour=result.hour, minute=result.minute)
  return result



