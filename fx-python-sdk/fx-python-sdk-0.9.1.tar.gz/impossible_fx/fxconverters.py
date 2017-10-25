"""
	member converters for Impossible FX API
"""

import datetime

import fractions

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_datetime( str_or_datetime ):
	if isinstance( str_or_datetime, basestring ):
		# noinspection PyTypeChecker
		return datetime.datetime.strptime( str_or_datetime, DATETIME_FORMAT )
	elif isinstance( str_or_datetime, datetime.datetime ):
		return str_or_datetime
	raise TypeError( "illegal type %s for 'to_datetime()'" % type( str_or_datetime ) )


def to_fraction( pair ):
	if pair:
		return fractions.Fraction( *pair )
	return None


