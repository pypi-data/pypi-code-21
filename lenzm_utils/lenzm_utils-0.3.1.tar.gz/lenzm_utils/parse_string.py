"""Parse different types of strings."""

import decimal


def money(money_string: str) -> decimal.Decimal:
	"""Parse a string representing some amount of money into a Decimal.

	Args:
		money_string (str): The string to try to parse

	Returns:
		A Decimal that is the amount of money.
	"""
	if not money_string:
		return decimal.Decimal(0)
	if money_string.startswith('$'):
		money_string = money_string[1:]
	money_string = money_string.replace(',', '')
	return decimal.Decimal(money_string)


def accounting(s: str) -> decimal.Decimal:
	"""Parse a string using accounting format (parenthesis for neg amounts)."""
	s = s.strip()
	if not s or s == '-':
		return decimal.Decimal(0)
	if s[0] == '(' and s[-1] == ')':
		s = '-' + s[1:-1]
	return decimal.Decimal(s)


def percent_to_float(s: str) -> float:
	"""Parse a percentage string into a float."""
	s = s.strip()
	if s.endswith('%'):
		s = s[:-1]
	return float(s) / 100.0


def percent_to_decimal(s: str, blank_return_value=None) -> decimal.Decimal:
	s = s.strip()
	if s.endswith('%'):
		s = s[:-1]
	if s == '':
		return blank_return_value
	return decimal.Decimal(s) / 100
