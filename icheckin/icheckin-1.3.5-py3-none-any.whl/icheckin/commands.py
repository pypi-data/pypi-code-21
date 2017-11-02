import os
from os.path import exists
from icheckin import constants
from collections import OrderedDict

#################################################

def _help():
	print(_usage()+'\n')
	print(_details())

def _save(cred, test=False):
	if not test:
		path = constants.PATH
	else:
		path = constants.TEST_PATH
	with open(path, 'w') as file:
		file.write(constants.KEYWORD_1+'\n')
		file.write(cred[0]+'\n\n')
		file.write(constants.KEYWORD_2+'\n')
		file.write(cred[1]+'\n')
	print('success: credentials saved to %s' % path)

def _remove(test=False):
	if not test:
		path = constants.PATH
	else:
		path = constants.TEST_PATH
	if exists(path):
		os.remove(path)
		print('success: %s removed' % path)
	else:
		print('error: %s does not exist' % path)

commands = OrderedDict()
commands['-h'] = {
	'alt'	: '--help',
	'info': 'Display help for command-line tools',
	'action': _help,
	'params': []
}
commands['-s'] = {
	'alt': '--save',
	'info': 'Save credentials',
	'action': _save,
	'params': ['student id', 'password']	
}
commands['-r'] = {
	'alt': '--remove',
	'info': 'Remove saved credentials',
	'action': _remove,
	'params': []	
}

#################################################

def process(args):
	''' 
	Process commands and carry out operations
	-> True	: Command executed
	-> False : Error with command or parameters
	''' 
	# Extract command and parameters
	cmd = args[0]
	if len(args) > 1:
		params = args[1:]
	else:
		params = []
	# Check command
	exists = False
	for command in commands.keys():
		if cmd == command:
			exists = True
		elif cmd == commands[command]['alt']:
			cmd = command
			exists = True
	if exists:
		# Check parameters
		parameters = commands[cmd]['params']
		if len(params) == len(parameters):
			# Execute command
			action = commands[cmd]['action']
			if len(params) == 0:
				action()
			else:
				action(params)
			return True
		else:
			# Invalid parameters
			print('error: invalid parameters')
			error = 'command: icheckin %s' % cmd
			for parameter in parameters:
				error += ' <%s>' % parameter
			print(error)
			return False
	else:
		# Invalid command
		print('unknown command: %s' % cmd)
		print(_usage())
		return False

def _usage():
	''' -> str	: Formatted usage ''' 
	head = 'usage: icheckin'
	usage = head
	for command in commands.keys():
		chunk = '%s' % command
		alt = commands[command]['alt']
		if alt != '':
			chunk += ' | %s' % alt
		params = commands[command]['params']
		for i in range(len(params)):
			chunk += ' <%s>' % params[i]
		chunk = ' [%s]' % chunk
		# Formatting
		buffer = usage + chunk
		if len(buffer.split('\n')[-1]) > 80:
			usage = '%s\n%s%s' % (usage, ' '*len(head), chunk)
		else:
			usage = buffer
	return usage

def _details():
	''' -> str	: Formatted details'''
	names = []
	infos = []
	for command in commands.keys():
		name = '   %s' % command
		alt = commands[command]['alt']
		if alt != '':
			name += ', %s' % alt
		names.append(name)
		infos.append(commands[command]['info'])
	a = max(list(map(lambda x: len(x), names))) + 3
	lines = []
	for i in range(len(names)):
		# Right pad name
		b = len(names[i])
		pad = a - b
		line = '%s%s' % (names[i], ' '*(pad-1))
		# Format info
		right = 80 - a
		for word in infos[i].split():
			buffer = '%s %s' % (line, word)
			if len(buffer) > 80:
				lines.append(line+'\n')
				line = '%s%s' % (' '*a, word)
			else:
				line = buffer
		lines.append(line+'\n')
	return ''.join(lines).strip('\n')

