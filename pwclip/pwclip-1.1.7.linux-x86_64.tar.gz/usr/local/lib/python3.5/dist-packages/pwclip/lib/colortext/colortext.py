# *- coding: utf-8 -*-
"""
text colorisation functions  due to extendet use of the python3 print
function this is for python3 only
"""
from os import name as osname
from sys import stdout, stderr
__echo = stdout.write
__puke = stderr.write

# get color escape sequence from string
if osname == 'nt':
	# color faker function for windows compatibility
	def __colorize(color, text): del color ;return text
else:
	def __colorize(color, text):
		"""colortag prepending and end-tag appending function"""
		string = '\033['
		if len(color) == 4:
			color = color[1:]
			string = '%s;01;'%(string)
		if color == 'gre':
			string = '%s30m'%(string)
		if color == 'red':
			string = '%s31m'%(string)
		if color == 'grn':
			string = '%s32m'%(string)
		if color == 'yel':
			string = '%s33m'%(string)
		if color == 'blu':
			string = '%s34m'%(string)
		if color == 'vio':
			string = '%s35m'%(string)
		if color == 'cya':
			string = '%s36m'%(string)
		if color == 'whi':
			string = '%s37m'%(string)
		colortext = '%s%s\033[0m'%(string, text)
		return colortext


# define 2 functions for each color
# one for normal and one for bold text

def blu(text):
	"""function for color blue"""
	return __colorize('blu', text)
def bblu(text):
	"""function for color boldblue"""
	return __colorize('bblu', text)

def cya(text):
	"""function for color cyan"""
	return __colorize('cya', text)
def bcya(text):
	"""function for color boldcyan"""
	return __colorize('bcya', text)

def gre(text):
	"""function for color grey"""
	return __colorize('gre', text)
def bgre(text):
	"""function for color boldgrey"""
	return __colorize('bgre', text)

def grn(text):
	"""function for color green"""
	return __colorize('grn', text)
def bgrn(text):
	"""function for color boldgreen"""
	return __colorize('bgrn', text)

def red(text):
	"""function for color red"""
	return __colorize('red', text)
def bred(text):
	"""function for color boldred"""
	return __colorize('bred', text)

def vio(text):
	"""function for color violet"""
	return __colorize('vio', text)
def bvio(text):
	"""function for color boldviolet"""
	return __colorize('bvio', text)

def whi(text):
	"""function for color white"""
	return __colorize('whi', text)
def bwhi(text):
	"""function for color boldwhite"""
	return __colorize('bwhi', text)

def yel(text):
	"""function for color guess what?  yellow ;)"""
	return __colorize('yel', text)
def byel(text):
	"""function for color and you already guessed it... boldyellow"""
	return __colorize('byel', text)

# functions for some high frequent use cases:
def abort(*messages):
	"""
	prints all text in blu by using STDOUT but also kills its
	parent processes and returns 0 (OK) instead of 1 (ERROR)
	by default used for aborting on STRG+C (see message,
	for "KeyboardInterrupt" exceptions)
	"""
	if not messages:
		messages = ('\naborted by keystroke', )
	msgs = []
	for msg in messages:
		if (messages.index(msg) % 2) == 0:
			msgs.append(blu(msg))
		else:
			msgs.append(yel(msg))
	__echo('%s\n'%' '.join(msg for msg in msgs))
	exit(1)

def error(*args, **kwargs):
	"""
	while i most often want to display error texts which heave
	one or more primary causes i want the text parts printed
	in red and the causes printed in yellow as follows
	"""
	delim = ' '
	errfile = ''
	errline = ''
	buzzword = 'ERROR:'
	if 'file' in kwargs.keys():
		errfile = '%s:'%(kwargs['file'])
	if 'line' in kwargs.keys():
		errline = '%s:'%(kwargs['line'])
	if 'warn' in kwargs.keys():
		buzzword = 'WARNING:'
	if 'sep' in kwargs.keys():
		delim = kwargs['sep']
	msgs = [errfile+errline+red(buzzword)]
	for arg in args:
		if (args.index(arg) % 2) == 0:
			msgs.append(red(arg))
		else:
			msgs.append(yel(arg))
	__puke('%s\n'%str(delim).join(msg for msg in msgs))

def fatal(*args, **kwargs):
	"""
	does exactly the same as "error" except it prints texts
	in bold and kills its parent processes
	"""
	errfile = ''
	errline = ''
	if 'file' in kwargs.keys():
		errfile = '%s:'%(kwargs['file'])
	if 'line' in kwargs.keys():
		errline = '%s: '%(kwargs['line'])
	msgs = ['%s%s%s'%(errfile, errline, bred('FATAL: '))]
	for arg in args:
		if (args.index(arg) % 2) == 0:
			msgs.append(bred(arg))
		else:
			msgs.append(yel(arg))
	__puke('%s\n'%''.join(msg for msg in msgs))
	exit(1)

def tabs(dat, ind=0, ll=80):
	"""string indentations on newline"""
	return '\n'.join(
        '%s%s'%(' '*ind, dat[i:int(i+ll)]) for i in range(0, len(dat), ll))

def tabl(dats, ind=0, iind=0):
	"""list to string with indentations"""
	tabbl = ''
	for i in dats:
		if isinstance(i, (tuple, list)):
			iind = int(max(len(i) for i in dats)+ind)
			tabbl = '%s\n%s'%(tabbl, tabl(i, iind))
			continue
		tabbl = '%s\n%s%s'%(tabbl, ' '*ind, i)
	return tabbl.lstrip('\n')

def tabd(dats, ind=0, iind=0):
	"""
	this is a function where i try to guess the best indentation for text
	representation of keyvalue paires with best matching indentation
	e.g:
	foo         = bar
	a           = b
	blibablubb  = bla
	^^indent "bar" and "b" as much as needed ("add" is added to each length)
	"""
	try:
		lim = int(max(len(str(k)) for k in dats if k)+int(ind))
	except ValueError:
		return dats
	tabbd = ''
	try:
		for (key, val) in sorted(dats.items()):
			spc = ' '*int(lim-len(str(key)))
			if val and isinstance(val, dict):
				tabbd = '%s\n%s%s:\n%s'%(tabbd, ' '*ind, key, tabd(
                    val, ind+int(iind if iind else 2), iind if iind else 2))
			else:
				tabbd = str('%s\n%s%s%s = %s'%(
                    tabbd, ' '*ind, key, spc, val)).strip('\n')
	except AttributeError:
		return tabl(dats, ind)
	return tabbd.strip('\n')

if __name__ == "__main__":
	# module debugging area
	#for i in (3, 4, 5):
	#	print(', '.join(m for m in dir() if len(m) == i))
	exit(1)
