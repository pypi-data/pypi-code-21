import contextlib
import functools
import operator


def product(iterable):
	return functools.reduce(operator.mul, iterable, 1)


def all_equal(iterable):
	try:
		value = first(iterable)
	except ValueError:
		return True
	for v in iterable:
		if v != value:
			return False
	return True


def one(iterable):
	"""Return the single element in iterable, raise an error if there isn't exactly one element."""
	item = None
	iterator = iter(iterable)
	try:
		item = next(iterator)
	except StopIteration:
		raise ValueError('Iterable is empty, must contain one item')
	try:
		next(iterator)
	except StopIteration:
		return item
	else:
		raise ValueError('Iterable contains multiple items, must contain exactly one.')


def first(iterable):
	for item in iterable:
		return item
	raise ValueError('Iterable is empty')


def last(iterable):
	return first(reversed(iterable))


def nth(iterable, n, key=None):
	if n < 0:
		iterable = reversed(iterable)
		n = -n - 1
	for index, elem in enumerate(iterable):
		if index == n:
			return elem
	raise ValueError('Iterable is not long enough')


def count(iterable):
	with contextlib.suppress(TypeError):
		return len(iterable)
	i = 0
	for elem in iterable:
		i += 1
	return i


def match_any(res, string):
	"""Return if a string matches any of a list of regular expressions.

	Args:
		string (str): The string that you want to check.
		res: An Iterable of regular expressions to check.

	Returns:
		True if any of the regexes in res matches string, otherwise False.
	"""
	for regex in res:
		if regex.match(string):
			return True
	return False
