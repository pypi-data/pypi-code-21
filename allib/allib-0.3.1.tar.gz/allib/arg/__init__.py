import sys

from .spec import ArgumentSpec
from .parser import parse_from_spec


class CommandLineInterface:
	def __init__(self, spec: ArgumentSpec):
		self.spec = spec

	def parse_args(self, args=None):
		if args is None:
			args = sys.argv[1:]
		return parse_from_spec(self.spec, args)
