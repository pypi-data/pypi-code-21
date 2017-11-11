from .spec import ValueOption


def add_value(add_to, item, value):
	value = item.type(value)
	if item.multiple:
		if item not in add_to:
			add_to[item] = []
		add_to[item].append(value)
	else:
		add_to[item] = value


def find_matching_choice(arg, choices):
	matches = []
	for choice in choices:
		if arg == choice:
			return arg
		if choice.startswith(arg):
			matches.append(choice)
	if len(matches) > 1:
		raise ValueError('ambiguous argument %r - %r' % (arg, matches))
	return matches[0]


class ParseResult:
	def __init__(self):
		self.options = {}
		self.arguments = {}

	def combine(self):
		ret = {}
		for option, value in self.options.items():
			ret[option.name] = value
		for argument, value in self.arguments.items():
			ret[argument.name] = value
		return ret


def parse_from_spec(spec, args):
	arglen = len(args)
	i = 0
	argument_i = 0
	result = ParseResult()

	while i < arglen:
		arg = args[i]

		if arg.startswith('-'):
			value = None
			if '=' in arg:
				flag, value = arg.split('=', 1)
			else:
				flag = args[i]
			option = spec.option_map[flag]
			if isinstance(option, ValueOption):
				if not value:
					value = args[i + 1]
					i += 1
			else:
				value = True
			add_value(result.options, option, value)
		else:
			argument = spec.arguments[argument_i]
			if argument.choices:
				arg = find_matching_choice(arg, argument.choices)
			argument_i += 1
			add_value(result.arguments, argument, arg)

		i += 1

	return result.combine()
