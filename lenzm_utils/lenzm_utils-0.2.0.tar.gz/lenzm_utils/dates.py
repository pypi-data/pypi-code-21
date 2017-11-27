"""date utils"""
import bisect
import calendar
from contextlib import suppress
from datetime import date, datetime, timedelta
import functools
from typing import Tuple

from collections_extended import setlist


(MON, TUE, WED, THU, FRI, SAT, SUN) = range(7)
weekends = (SAT, SUN)


def week_start(d: datetime, starts_on=SUN) -> date:
	"""Return the first day of the week for the passed date.

	Args:
		d (datetime.datetime or datetime.date): When to get the week start for.
		starts_on: The day of the week that the week starts on.

	Returns:
		A datetime.date object for the first day of the week containing d.
	"""
	if isinstance(d, datetime):
		d = d.date()
	else:
		assert isinstance(d, date)
	days = (d.weekday() + 7 - starts_on) % 7
	d -= timedelta(days=days)
	return d


def workday_diff(start_date: datetime, end_date: datetime, holidays=None) -> float:
	"""Calculate the number of working days between two dates.
	"""
	assert isinstance(start_date, datetime)
	assert isinstance(end_date, datetime)
	if not holidays:
		holidays = setlist()
	else:
		holidays = setlist(sorted(holidays))
	if end_date < start_date:
		return -workday_diff(start_date=end_date, end_date=start_date, holidays=holidays)
	elif end_date == start_date:
		return 0
	# first full day is inclusive
	first_full_day = (start_date + timedelta(days=1)).date()
	# last full day is exclusive
	last_full_day = end_date.date()
	if last_full_day > first_full_day:
		num_full_days = (last_full_day - first_full_day) / timedelta(days=1)
		full_weeks, extra_days = divmod(num_full_days, 7)
		full_weeks = int(full_weeks)
		extra_days = int(extra_days)
		num_full_days -= full_weeks * len(weekends)
		# subtract out any working days that fall in the 'shortened week'
		for d in range(extra_days):
			if (first_full_day + timedelta(d)).weekday() in weekends:
				num_full_days -= 1
		# subtract out any holidays
		start_index = bisect.bisect_left(holidays, start_date.date())
		stop_index = bisect.bisect_right(holidays, end_date.date())
		for d in holidays[start_index:stop_index]:
			if d.weekday() not in weekends and first_full_day <= d < last_full_day:
				num_full_days -= 1
	else:
		num_full_days = 0

	def exclude_day(d):
		return d.weekday() in weekends or d in holidays

	partial_days = 0.0
	if end_date.date() == start_date.date():
		if not exclude_day(start_date):
			partial_days = (end_date - start_date) / timedelta(days=1)
	else:
		if not exclude_day(start_date):
			start_date_eod = datetime(first_full_day.year, first_full_day.month, first_full_day.day)
			partial_days += (start_date_eod - start_date) / timedelta(days=1)
		if not exclude_day(end_date):
			end_date_eod = datetime(last_full_day.year, last_full_day.month, last_full_day.day)
			partial_days += (end_date - end_date_eod) / timedelta(days=1)
	return partial_days + num_full_days


def midnight(d: date) -> datetime:
	"""Given a datetime.date, return a datetime.datetime of midnight."""
	if d is None:
		return None
	return datetime(d.year, d.month, d.day)


def past_complete_weeks(
	num_weeks: int,
	today=None,
	week_starts_on=SUN,
	) -> Tuple[datetime, datetime]:
	"""Return a tuple marking the beginning and end of the past number of weeks.

	Args:
		num_weeks (int): The number of weeks
	Returns:
		beg (datetime), end (datetime)
	"""
	if today is None:
		today = date.today()
	end = week_start(today, starts_on=week_starts_on)
	num_days = 7 * num_weeks
	start = end - timedelta(days=num_days)
	return start, end


@functools.total_ordering
class Month():

	def __init__(self, year, month):
		if not 0 < month <= 12:
			raise ValueError('Invalid month')
		self.year = int(year)
		self.month = int(month)

	def first(self):
		"""Return a datetime.date object for the first of the month."""
		return self.date(1)

	def first_datetime(self):
		"""Return a datetime.date object for the first of the month."""
		return self.datetime(1)

	def first_string(self):
		return self.first().strftime('%m/%d/%Y')

	def mid(self):
		"""Return a datetime.date object for the 15th of the month."""
		return self.date(15)

	def mid_datetime(self):
		"""Return a datetime.date object for the 15th of the month."""
		return datetime(self.year, self.month, 15)

	def mid_string(self):
		return self.mid().strftime('%m/%d/%Y')

	def last(self):
		return date(self.year, self.month, self.num_days())

	def num_days(self):
		return calendar.monthrange(self.year, self.month)[1]

	def date(self, day):
		"""Return a date for the day of the month.

		num can be a negative number to count back from the end of the month.
		eg. date(-1) is the last day of the month.
		"""
		if day < 0:
			day += self.num_days() + 1
		return date(self.year, self.month, day)

	def datetime(self, day, *args, **kwargs):
		return datetime(self.year, self.month, day, *args, **kwargs)

	def pace(self, d=None):
		"""Return how far through this month d is.

		If d isn't passed use datetime.now()
		"""
		if d is None:
			d = datetime.now()
		if self.month == d.month and self.year == d.year:
			days_into_month = (d - self.first_datetime()) / timedelta(days=1)
			return 1.0 - (days_into_month / self.num_days())
		elif self.year > d.year or (self.year == d.year and self.month > d.month):
			return 1.0
		else:
			return 0.0

	def next(self):
		if self.month == 12:
			return Month(self.year + 1, 1)
		else:
			return Month(self.year, self.month + 1)

	@classmethod
	def from_date(cls, d):
		"""Create a Month from a date(time) object."""
		if not d:
			return None
		return cls(d.year, d.month)

	def __eq__(self, other):
		return isinstance(other, Month) and (self.year, self.month) == (other.year, other.month)

	def __lt__(self, other):
		try:
			return (self.year, self.month) < (other.year, other.month)
		except AttributeError:
			return NotImplemented

	def __sub__(self, other):
		"""Return the number of months between two months."""
		return 12 * (self.year - other.year) + self.month - other.month

	@staticmethod
	def iter(start, end=None):
		"""Generate months between passed months.

		Args:
			start: The first month to yield.
			end: The final month to yield. If None, yield infinitely.

		Yields:
			Months between the passed values inclusive.
		"""
		month = start
		while end is None or month <= end:
			yield month
			month = month.next()

	def days(self):
		"""Generate the dates in this month."""
		for i in range(self.num_days()):
			yield self.date(i + 1)


# Parsing

def parse_iso_date_with_colon(date_string):
	"""Parse a date in ISO format with a colon in the timezone.

	For example: 2014-05-01T15:08:00-07:00
	Or if the timezone is missing, parse that:
	For example: 2014-05-01T15:08:00
	"""
	with suppress(ValueError):
		return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
	with suppress(ValueError):
		return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
	try:
		last_colon_index = date_string.rindex(':')
	except ValueError:
		raise ValueError(date_string)
	clean = date_string[:last_colon_index] + date_string[last_colon_index + 1:]
	return datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S%z')


def parse_date_missing_zero_padding(date_string, sep='/', order='mdy', min_year=2000):
	"""Parse dates without zero padding like 3/1/14.

	If min_year is set, then the year string can be two digits and is parsed as
	the year >= min_year with the last two digits as the passed year.

	Args:
		date_string (str): String to parse
		sep (str): The separator between month, day and year
		order (str): 'm', 'd' and 'y' indicating the order the month, day and year
		min_year (str): For two digit years, use the next year after min_year
	"""
	if len(order) != 3 or set(order) != set('mdy'):
		raise ValueError('Invalid order')
	strings = date_string.split(sep)
	if len(strings) != 3:
		raise ValueError('date_string does not contain 3 values')
	day = int(strings[order.index('d')])
	month = int(strings[order.index('m')])
	year = int(strings[order.index('y')])
	if year < min_year:
		if year < 0 or year >= 100:
			raise ValueError
		year = 100 * (min_year // 100) + year
		if year <= min_year:
			year += 100
	return date(year, month, day)
