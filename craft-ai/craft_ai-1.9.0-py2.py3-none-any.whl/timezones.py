import re

_TIMEZONE_REGEX = re.compile(r"^([+-](2[0-3]|[01][0-9])(:?[0-5][0-9])?|Z)$")

TIMEZONES = {
  "UTC": "+00:00",
  "GMT": "+00:00",
  "BST": "+01:00",
  "IST": "+01:00",
  "WET": "+00:00",
  "WEST": "+01:00",
  "CET": "+01:00",
  "CEST": "+02:00",
  "EET": "+02:00",
  "EEST": "+03:00",
  "MSK": "+03:00",
  "MSD": "+04:00",
  "AST": "-04:00",
  "ADT": "-03:00",
  "EST": "-05:00",
  "EDT": "-04:00",
  "CST": "-06:00",
  "CDT": "-05:00",
  "MST": "-07:00",
  "MDT": "-06:00",
  "PST": "-08:00",
  "PDT": "-07:00",
  "HST": "-10:00",
  "AKST": "-09:00",
  "AKDT": "-08:00",
  "AEST": "+10:00",
  "AEDT": "+11:00",
  "ACST": "+09:30",
  "ACDT": "+10:30",
  "AWST": "+08:00"
}

def is_timezone(value):
  result_reg_exp = _TIMEZONE_REGEX.match(value) is not None
  result_abbreviations = value in TIMEZONES
  return result_reg_exp or result_abbreviations

def timezone_offset_in_sec(timezone):
  if timezone in TIMEZONES:
    timezone = TIMEZONES[timezone]
  if len(timezone) > 3:
    timezone = timezone.replace(":", "")
    offset = (int(timezone[-4:-2]) * 60 + int(timezone[-2:])) * 60
  else:
    offset = (int(timezone[-2:]) * 60) * 60

  if timezone[0] == "-":
    offset = -offset

  return offset
