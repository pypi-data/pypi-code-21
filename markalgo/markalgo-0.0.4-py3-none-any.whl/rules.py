#!/usr/bin/env python3
"Work with replacement rules"

from collections import namedtuple

class ReplacementRule(namedtuple('ReplacementRule', [
														'pattern',
														'replacement',
														 'final'])):
	"""Rule for string replacing"""
	__slots__ = ()


	def __new__(cls, pattern="", replacement="", is_final=False):
		if not pattern:
			raise WrongInputError("Pattern is empty.")
		return super(cls, ReplacementRule).__new__(
													cls,
													pattern,
													replacement,
													bool(is_final))


	def __repr__(self):
		_final = "final" if self.final else "non-final"
		return "{2} rule for replacing {0} with {1}".format(self.pattern,
															self.replacement,
															_final)

	def __eq__(self, other):
		return self.pattern == other.pattern\
			and self.replacement == other.replacement\
			and self.final == other.final

	def __hash__(self):
		return hash((self.pattern, self.replacement, self.final))


	def process_text(self, text):
		"""Find first occurence of pattern in given text and replace it
			Return changed text and True, if occurence was found
			or orignal text and False overwise
		"""

		if self.pattern in text:
			return(text.replace(self.pattern, self.replacement, 1), True)
		else:
			return(text, False)


class RulesError(Exception):
	"""Base class for exceptions in this module."""
	pass

class WrongInputError(RulesError):
	"""Exception raised for errors in the input.

	Attributes:
		expression -- input expression in which the error occurred
		message -- explanation of the error
	"""

	def __init__(self, message):
		RulesError.__init__(self, message)
		self.message = message


def create_rules(pairs):
	"""Create non-final rules from given non-empty list of tuples"""

	if len(pairs) < 1:
		raise WrongInputError("No values were given")

	_rules = []
	for pair in pairs:
		_rules.append(ReplacementRule(pair[0], pair[1]))

	return _rules


def read_all_rules_from_csv_file(rule_file):
	"Parse csv file and return list of rules"
	rules = []
	for rule_string in rule_file:
		rule_string = rule_string.rstrip("\n")
		rules.append(_parse_csv_rule(rule_string))
	return rules


def _parse_csv_rule(csvrule):
	splitted = csvrule.split(";")

	return ReplacementRule(
							pattern=splitted[0],
							replacement=splitted[1],
							is_final=_is_mark_of_final(splitted[2]))

_FINAL_KEYWORD = "final"
def _is_mark_of_final(source):
	if source is None:
		return False
	return str(source).lower() == _FINAL_KEYWORD
