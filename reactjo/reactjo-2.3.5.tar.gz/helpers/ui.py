# Usage
# Pass the question as a string, without "(y/n)"
# (optional) pass a default of either "y" or "n"
# if no default is passed, then it's required,
# and process repeats until a valid answer is given
# e.g. boolean_input("Do you like cats", 'n') defaults to 'n'
from helpers.compose import paint
def boolean_input(string, default = False):
	answer = False

	# If input is optional
	if default in ['y','n']:
		def ask_optional():
			answer = input(
				paint(string + " (y/n default " + default + "): ")).lower()
			if answer == 'y':
				return True
			elif answer == 'n':
				return False
			elif answer == '':
				return default == 'y'
			else:
				ask_optional()
		return ask_optional()

	# If input is required
	while answer not in ['y','n']:
		answer = input(paint(string + " (y/n): ")).lower()
	return answer == 'y'

# Usage
# Pass the question as a string
# (optional) pass a default value
# e.g. string_input("What's your name") No default.
def string_input(string, default = ""):
	answer = ""

	# If input is optional
	if default != "":
		question = paint(string + ' (default: ' + default + '): ')
		answer = input(question)
		if answer == "":
			return default
		else:
			return str(answer)

	# If input is required
	while answer == "" or answer == False:
		answer = input(paint(string + ": "))

	return str(answer)

# Use like string_input, but for integers
def int_input(string, default = False, data = {}):
	string = paint(string)
	return int(string_input(string, default))

# Use like string_input, but for floats
def float_input(string, default = False):
	string = paint(string)
	return float(string_input(string, default))

# Same as above, but takes a list of options. e.g. ['foo','bar']
# Calculates everything in lowercase,
# but returns same case specified by selected option
def options_input(string, options, default = False):
	string = paint(string)
	answer = ""
	print(" ")
	print(paint('Available options:'))
	lower_options = []
	for option in options:
		print(paint(option, 'yellow'))
		lower_options.append(option.lower())
	print(" ")

	def cap_option(value):
		i = lower_options.index(value)
		return options[i]
	lower_default = default.lower() if default != False else False
	# If input is optional
	if lower_default in lower_options:
		answer = input(paint(f'{string} (default: {default}): ')).lower()
		if answer in lower_options:
			return cap_option(answer)
		else:
			return default

	# If input is required
	while answer not in lower_options:
		answer = input(string + ': ').lower()
	return cap_option(answer)
