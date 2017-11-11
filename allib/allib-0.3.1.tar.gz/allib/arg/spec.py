def guess_short_flag(long_flag):
	return '-' + long_flag.lstrip('-')[0]


def guess_name(long_flag):
	return long_flag.strip('-').replace('-', '_')


class Argument:
	def __init__(self, name, type=str, optional=False, multiple=False, choices=None):
		self.name = name
		self.type = type
		self.optional = optional
		self.multiple = multiple
		self.choices = choices


class Option:
	def __init__(self, long_flag, short_flag=None, name=None):
		self.long_flag = long_flag
		self.short_flag = short_flag or guess_short_flag(long_flag)
		self.name = name or guess_name(long_flag)
		self.type = bool
		self.multiple = False


class ValueOption(Option):
	def __init__(self, long_flag, short_flag=None, name=None, type=str, multiple=False):
		super().__init__(long_flag=long_flag, short_flag=short_flag, name=name)
		self.type = type
		self.multiple = multiple


class ArgumentSpec:
	def __init__(self, options=[], arguments=[]):
		self.options = []
		self.option_map = {}
		self.arguments = []
		for option in options:
			self.add_option(option)
		for argument in arguments:
			self.add_argument(argument)

	def add(self, item):
		if isinstance(item, Option):
			self.add_option(item)
		elif isinstance(item, Argument):
			self.add_argument(item)
		else:
			raise TypeError('can only add Option or Argument')

	def add_option(self, option: Option):
		self.options.append(option)
		for flag in (option.short_flag, option.long_flag):
			if flag in self.option_map:
				exc_msg = "flag %r already taken by %r" % (
					flag, self.option_map[flag]
				)
				raise ValueError(exc_msg)
			self.option_map[flag] = option

	def add_argument(self, argument: Argument):
		self.arguments.append(argument)
