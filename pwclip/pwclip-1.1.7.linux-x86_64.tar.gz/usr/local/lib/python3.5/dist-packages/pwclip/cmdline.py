#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
"""pwclip main program"""
# global & stdlib imports
try:
	from os import fork
except ImportError:
	def fork(): """fork faker function""" ;return 0

from os import environ, path, remove, name as osname

from subprocess import call

from argparse import ArgumentParser

from socket import gethostname as hostname

from time import sleep

from getpass import getpass

from yaml import load

try:
	import readline
except ImportError:
	pass

# local relative imports
from colortext import blu, bgre, tabd, error, fatal

from system import copy, paste, xinput, xgetpass, xyesno, xnotify, which

# first if on windows and gpg.exe cannot be found in PATH install gpg4win
if osname == 'nt' and not which('gpg.exe'):
	if not xyesno('gpg4win is mandatory! Install it?'):
		exit(1)
	import wget
	src = 'https://files.gpg4win.org/gpg4win-latest.exe'
	trg = path.join(environ['TEMP'], 'gpg4win.exe')
	wget.download(src, out=trg)
	try:
		call(trg)
	except TimeoutError:
		exit(1)
	finally:
		remove(trg)

from secrecy import GPGTool, PassCrypt, ykchalres

from pwclip.__pkginfo__ import version

def forkwaitclip(text, poclp, boclp, wait=3):
	"""clipboard forking, after time resetting function"""
	if fork() == 0:
		try:
			copy(text, mode='pb')
			sleep(int(wait))
		except (KeyboardInterrupt, RuntimeError):
			exit(1)
		finally:
			copy(poclp, mode='p')
			copy(boclp, mode='b')
	exit(0)

def _keycheck_(mode, kwargs):
	gpg = GPGTool(**kwargs)
	if gpg.findkey('', secret=True):
		return
	gpg.genkeys(mode)

def __passreplace(pwlist):
	"""returnes a string of asterisk's as long as the password is"""
	__pwcom = ['*'*len(pwlist[0])]
	if len(pwlist) > 1:
		__pwcom.append(pwlist[1])
	return __pwcom

def __dictreplace(pwdict):
	"""password => asterisk replacement function"""
	__pwdict = {}
	for (usr, ent) in pwdict.items():
		if isinstance(ent, dict):
			__pwdict[usr] = {}
			for (u, e) in ent.items():
				__pwdict[usr][u] = __passreplace(e)
		elif ent:
			__pwdict[usr] = __passreplace(ent)
	return __pwdict

def _printpws_(pwdict, insecure=False):
	"""password printer with in/secure option"""
	if not insecure:
		pwdict = __dictreplace(pwdict)
	print(tabd(pwdict))
	exit(0)

def __confcfgs():
	"""config parser function"""
	_me = path.basename(path.dirname(__file__))
	cfg = path.expanduser('~/.config/%s.yaml'%_me)
	try:
		with open(cfg, 'r') as cfh:
			cfgs = load(cfh.read())
	except FileNotFoundError:
		cfgs = {}
	try:
		cfgs['time'] = environ['PWCLIPTIME']
	except KeyError:
		cfgs['time'] = 3 if 'time' not in cfgs.keys() else cfgs['time']
	try:
		cfgs['ykslot'] = environ['YKSLOT']
	except KeyError:
		cfgs['ykslot'] = 2 if 'ykslot' not in cfgs.keys() else cfgs['ykslot']
	try:
		cfgs['ykser'] = environ['YKSERIAL']
	except KeyError:
		cfgs['ykser'] = None
	try:
		cfgs['binary']
	except KeyError:
		cfgs['binary'] = 'gpg2'
		if osname == 'nt':
			cfgs['binary'] = 'gpg'
	try:
		cfgs['user'] = environ['USER']
	except KeyError:
		cfgs['user'] = environ['USERNAME']
	if 'crypt' not in cfgs.keys():
		cfgs['crypt'] = path.expanduser('~/.passcrypt')
	elif 'crypt' in cfgs.keys() and cfgs['crypt'].startswith('~'):
		cfgs['crypt'] = path.expanduser(cfgs['crypt'])
	if 'plain' not in cfgs.keys():
		cfgs['plain'] = path.expanduser('~/.pwd.yaml')
	elif 'plain' in cfgs.keys() and cfgs['plain'].startswith('~'):
		cfgs['plain'] = path.expanduser(cfgs['plain'])
	return cfgs

def gui(typ='pw'):
	"""gui wrapper function to not run unnecessary code"""
	poclp, boclp = paste('pb')
	cfgs = __confcfgs()
	if typ == 'yk':
		__in = xinput()
		__res = ykchalres(__in, cfgs['ykslot'], cfgs['ykser'])
		if not __res:
			exit(1)
		forkwaitclip(__res, poclp, boclp, cfgs['time'])
	_keycheck_('gui', cfgs)
	pcm = PassCrypt(*('aal', 'rem', ), **cfgs)
	__in = xinput()
	if not __in: exit(1)
	__ent = pcm.lspw(__in)
	if __ent and __in:
		if __in not in __ent.keys() or not __ent[__in]:
			exit(1)
		__pc = __ent[__in]
		if __pc:
			if len(__pc) == 2:
				xnotify('%s: %s'%(__in, __pc[1]), cfgs['time'])
			poclp, boclp = paste('pb')
			forkwaitclip(__pc[0], poclp, boclp, cfgs['time'])

def cli():
	"""pwclip command line opt/arg parsing function"""
	cfgs = __confcfgs()
	pars = ArgumentParser() #add_help=False)
	pars.set_defaults(**cfgs)
	pars.add_argument(
        '--version',
        action='version', version='%(prog)s-v'+version)
	pars.add_argument(
        '-D', '--debug',
        dest='dbg', action='store_true', help='debugging mode')
	pars.add_argument(
        '-1',
        dest='gpv', action='store_const', const='1',
        help='force usage of gpg in version 1.x')
	pars.add_argument(
        '-A', '--all',
        dest='aal', action='store_true',
        help='switch to all users entrys (instead of current user only)')
	pars.add_argument(
        '-R',
        dest='rem', action='store_true',
        help='use remote backup given by --remote-host')
	pars.add_argument(
        '--remote-host',
        dest='rehost', metavar='HOST',
        help='use HOST for connections')
	pars.add_argument(
        '--remote-user',
        dest='reuser', metavar='USER',
        help='use USER for connections to HOST')
	pars.add_argument(
        '-s', '--show-passwords',
        dest='sho', action='store_true',
        help='switch to display passwords (replaced with * by default)')
	pars.add_argument(
        '-a', '--add',
        dest='add', metavar='ENTRY',
        help='add ENTRY (password will be asked interactivly)')
	pars.add_argument(
        '-c', '--change',
        dest='chg', metavar='ENTRY',
        help='change ENTRY (password will be asked interactivly)')
	pars.add_argument(
        '-d', '--delete',
        dest='rms', metavar='ENTRY', nargs='+',
        help='delete ENTRY(s) from the passcrypt list')
	pars.add_argument(
        '-l', '--list',
        nargs='?', dest='lst', metavar='PATTERN', default=False,
        help='search entry matching PATTERN if given otherwise list all')
	pars.add_argument(
        '--yaml',
        dest='yml', metavar='YAMLFILE',
        default=path.expanduser('~/.pwd.yaml'),
        help='set location of one-time password YAMLFILE to read & delete')
	pars.add_argument(
        '-p', '--passcrypt',
        dest='pcr', metavar='CRYPTFILE',
        default=path.expanduser('~/.passcrypt'),
        help='set location of CRYPTFILE to use for gpg features')
	pars.add_argument(
        '-r', '--recipients',
        dest='rcp', metavar='ID(s)',
        help='gpg-key ID(s) to use for ' \
             'encryption (string seperated by spaces)')
	pars.add_argument(
        '-u', '--user',
        dest='usr', metavar='USER', default=cfgs['user'],
        help='query entrys only for USER ' \
             '(defaults to current user, overridden by -A)')
	pars.add_argument(
        '-y', '--ykserial',
        nargs='?', dest='yks', metavar='SERIAL', default=False,
        help='switch to yubikey mode and optionally set SERIAL of yubikey')
	pars.add_argument(
        '-S', '--ykslot',
        dest='ysl', default=2, type=int, choices=(1, 2),
        help='set one of the two slots on the yubi-key (only useful for -y)')
	pars.add_argument(
        '-t',
        dest='time', default=3, metavar='seconds', type=int,
        help='time to wait before resetting clip (default is 3 max 3600)')
	args = pars.parse_args()
	__pargs = [a for a in [
        'aal' if args.aal else None,
        'dbg' if args.dbg else None,
        'rem' if args.sho else None,
        'sho' if args.sho else None] if a]
	__bin = 'gpg2'
	if args.gpv:
		__bin = args.gpv
	elif osname == 'nt':
		__bin = 'gpg'
	__pkwargs = {}
	__pkwargs['binary'] = __bin if osname != 'nt' else '%s.exe'%__bin
	if args.pcr:
		__pkwargs['crypt'] = args.pcr
	if args.rcp:
		__pkwargs['recvs'] = list(args.rcp.split(' '))
	if args.usr:
		__pkwargs['user'] = args.usr
	if args.yml:
		__pkwargs['plain'] = args.yml
	if hasattr(args, 'remote'):
		__pkwargs['remote'] = args.remote
	if hasattr(args, 'reuser'):
		__pkwargs['reuser'] = args.reuser
	if args.dbg:
		print(bgre(pars))
		print(bgre(tabd(args.__dict__, 2)))
		print(bgre(__pkwargs))

	if not path.isfile(args.yml) and \
          not path.isfile(args.pcr) and args.yks is False:
		with open(args.yml, 'w+') as yfh:
			yfh.write("""---\n%s:  {}"""%args.usr)

	poclp, boclp = paste('pb')
	if args.yks or args.yks is None:
		if 'YKSERIAL' in environ.keys():
			__ykser = environ['YKSERIAL']
		__ykser = args.yks if args.yks and len(args.yks) >= 6 else None
		__in = xinput()
		__res = ykchalres(__in, args.ysl, __ykser)
		if not __res:
			fatal('could not get valid response on slot ', args.ysl)
		forkwaitclip(__res, poclp, boclp, args.time)
	else:
		_keycheck_('cli', __pkwargs)
		pcm = PassCrypt(*__pargs, **__pkwargs)
		__ent = None
		if args.add:
			if not pcm.adpw(args.add):
				fatal('could not add entry ', args.add)
			_printpws_(pcm.lspw(args.add), args.sho)
		elif args.chg:
			if not pcm.chpw(args.chg):
				fatal('could not change entry ', args.chg)
			_printpws_(pcm.lspw(args.chg), args.sho)
		elif args.rms:
			for r in args.rms:
				if not pcm.rmpw(r):
					error('could not delete entry ', r)
			_printpws_(pcm.lspw(), args.sho)
		elif args.lst is not False:
			__ent = pcm.lspw(args.lst)
			if not __ent:
				fatal('could not decrypt')
			elif __ent and args.lst and not args.lst in __ent.keys():
				fatal(
                    'could not find entry for ',
                    args.lst, ' in ', __pkwargs['crypt'])
			elif args.lst and __ent:
				__pc = __ent[args.lst]
				if __pc:
					if len(__pc) == 2:
						xnotify(
                            '%s: %s'%(args.lst, __pc[1]), wait=args.time)
					forkwaitclip(__pc[0], poclp, boclp, args.time)
		else:
			__in = xinput()
			if not __in: exit(1)
			__ent = pcm.lspw(__in)
			if __ent and __in:
				if __in not in __ent.keys() or not __ent[__in]:
					fatal(
                        'could not find entry for ',
                        __in, ' in ', __pkwargs['crypt'])
				__pc = __ent[__in]
				if __pc:
					if len(__pc) == 2:
						xnotify('%s: %s'%(__in, __pc[1]), args.time)
					forkwaitclip(__pc[0], poclp, boclp, args.time)
		if __ent: _printpws_(__ent, args.sho)



if __name__ == '__main__':
	exit(1)
