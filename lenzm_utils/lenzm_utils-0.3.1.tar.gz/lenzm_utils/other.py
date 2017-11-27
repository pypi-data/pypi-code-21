"""util - simple functions needed in multiple modules"""
import functools
import urllib.parse



STATE_ABBRS = {
	'Alabama': 'AL',
	'Alaska': 'AK',
	'Arizona': 'AZ',
	'Arkansas': 'AR',
	'California': 'CA',
	'Colorado': 'CO',
	'Connecticut': 'CT',
	'Delaware': 'DE',
	'Florida': 'FL',
	'Georgia': 'GA',
	'Hawaii': 'HI',
	'Idaho': 'ID',
	'Illinois': 'IL',
	'Indiana': 'IN',
	'Iowa': 'IA',
	'Kansas': 'KS',
	'Kentucky': 'KY',
	'Louisiana': 'LA',
	'Maine': 'ME',
	'Maryland': 'MD',
	'Massachusetts': 'MA',
	'Michigan': 'MI',
	'Minnesota': 'MN',
	'Mississippi': 'MS',
	'Missouri': 'MO',
	'Montana': 'MT',
	'Nebraska': 'NE',
	'Nevada': 'NV',
	'New Hampshire': 'NH',
	'New Jersey': 'NJ',
	'New Mexico': 'NM',
	'New York': 'NY',
	'North Carolina': 'NC',
	'North Dakota': 'ND',
	'Ohio': 'OH',
	'Oklahoma': 'OK',
	'Oregon': 'OR',
	'Pennsylvania': 'PA',
	'Rhode Island': 'RI',
	'South Carolina': 'SC',
	'South Dakota': 'SD',
	'Tennessee': 'TN',
	'Texas': 'TX',
	'Utah': 'UT',
	'Vermont': 'VT',
	'Virginia': 'VA',
	'Washington': 'WA',
	'West Virginia': 'WV',
	'Wisconsin': 'WI',
	'Wyoming': 'WY',
	'American Samoa': 'AS',
	'District of Columbia': 'DC',
	'Federated States of Micronesia': 'FM',
	'Guam': 'GU',
	'Marshall Islands': 'MH',
	'Northern Mariana Islands': 'MP',
	'Palau': 'PW',
	'Puerto Rico': 'PR',
	'Virgin Islands': 'VI',
	'Armed Forces Americas': 'AA',
	'Armed Forces Europe': 'AE',
	'Armed Forces Pacific': 'AP',
	}


class no_autoflush(object):
	def __init__(self, session):
		self.session = session
		self.autoflush = session.autoflush

	def __enter__(self):
		self.session.autoflush = False

	def __exit__(self, type, value, traceback):
		self.session.autoflush = self.autoflush


class memoized_method(object):
	"""cache the return value of a method

	This class is meant to be used as a decorator of methods. The return value
	from a given method invocation will be cached on the instance whose method
	was invoked. All arguments passed to a method decorated with memoize must
	be hashable.

	If a memoized method is invoked directly on its class the result will not
	be cached. Instead the method will be invoked like a static method:
	class Obj(object):
		@memoize
		def add_to(self, arg):
			return self + arg
	Obj.add_to(1) # not enough arguments
	Obj.add_to(1, 2) # returns 3, result is not cached

	Based on:
	http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/
	"""
	def __init__(self, func):
		self.func = func

	def __get__(self, obj, objtype=None):
		if obj is None:
			return self.func
		return functools.partial(self, obj)

	def __call__(self, *args, **kw):
		obj = args[0]
		try:
			cache = obj.__cache
		except AttributeError:
			cache = obj.__cache = {}
		key = (self.func, args[1:], frozenset(kw.items()))
		try:
			res = cache[key]
		except KeyError:
			res = cache[key] = self.func(*args, **kw)
		except TypeError:
			# This happens if an argument is unhashable
			res = self.func(*args, **kw)
		return res


class classproperty(object):

	def __init__(self, fget):
		self.fget = fget

	def __get__(self, owner_self, owner_cls):
		return self.fget(owner_cls)


def valid_email_address(email):
	if not email or len(email) < 6:
		return False
	try:
		local, domain = email.split('@', 1)
	except ValueError:
		return False
	return local and domain and '.' in domain


def create_url(
	scheme='',
	path='',
	query='',
	fragment='',
	username=None,
	password=None,
	hostname=None,
	port=None,
	):
	"""Like urlib.parse.urlunsplit but build the netloc from parts."""
	if not hostname:
		raise ValueError('Need hostname')
	if port:
		netloc_fmt = '{hostname}:{port}'
	else:
		netloc_fmt = '{hostname}'
	if username:
		if password:
			netloc_fmt = '{username}:{password}@%s' % netloc_fmt
		else:
			netloc_fmt = '{username}@%s' % netloc_fmt
	elif password:
		raise ValueError('Cannot handle password without username')
	netloc = netloc_fmt.format(
		username=username,
		password=password,
		hostname=hostname,
		port=port,
		)
	return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
