#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""passcrypt module"""

from os import path, remove, environ, chmod

from shutil import copyfile

from yaml import load, dump

from paramiko.ssh_exception import SSHException

from colortext import bgre, tabd

from system import userfind

from net.ssh import SecureSHell

from secrecy.gpg import GPGTool

class PassCrypt(GPGTool, SecureSHell):
	"""passcrypt main class"""
	dbg = None
	aal = None
	sho = None
	try:
		user = userfind()
		home = userfind(user, 'home')
	except FileNotFoundError:
		user = environ['USERNAME']
		home = path.join(environ['HOMEDRIVE'], environ['HOMEPATH'])
	plain = path.join(home, '.pwd.yaml')
	crypt = path.join(home, '.passcrypt')
	recvs = []
	remote = ''
	reuser = user
	if 'GPGKEYS' in environ.keys():
		recvs = environ['GPGKEYS'].split(' ')
	elif 'GPGKEY' in environ.keys():
		recvs = recvs + [
            environ['GPGKEY']] if not environ['GPGKEY'] in recvs else []
	def __init__(self, *args, **kwargs):
		"""passcrypt init function"""
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if self.dbg:
			print(bgre(PassCrypt.__mro__))
			print(bgre(tabd(PassCrypt.__dict__, 2)))
			print(' ', bgre(self.__init__))
			print(bgre(tabd(self.__dict__, 4)))
		GPGTool.__init__(self, *args, **kwargs)
		SecureSHell.__init__(self, *args, **kwargs)
		if self.remote:
			self._copynews_()
		__weaks = self._readcrypt()
		try:
			with open(self.plain, 'r') as pfh:
				__newpws = load(pfh.read())
			if not self.dbg:
				remove(self.plain)
		except FileNotFoundError:
			__newpws = {}
		if __newpws:
			__weaks = __weaks if __weaks else {}
			for (k, v) in __newpws.items():
				__weaks[k] = v
		if __weaks != self._readcrypt():
			self._writecrypt(__weaks)
		self.__weaks = __weaks

	def _copynews_(self):
		"""copy new file method"""
		if self.dbg:
			print(bgre(self._copynews_))
		if self.remote:
			try:
				self.scpcompstats(
                    self.crypt, path.basename(self.crypt),
                    self.remote, self.reuser)
			except (FileNotFoundError, SSHException):
				pass

	def _chkcrypt(self):
		"""crypt file checker method"""
		if self.dbg:
			print(bgre(self._chkcrypt))
		if self._readcrypt() == self.__weaks:
			return True

	def _findentry(self, pattern, weakz=None):
		"""entry finder method"""
		if self.dbg:
			print(bgre(tabd({self._findentry: {'pattern': pattern}})))
		__weakz = weakz if weakz else self.__weaks
		for (u, p) in __weakz.items():
			if pattern == u or (
                  len(p) == 2 and len(pattern) > 1 and pattern in p[1]):
				return p

	def _readcrypt(self):
		"""read crypt file method"""
		if self.dbg:
			print(bgre(self._readcrypt))
		try:
			with open(self.crypt, 'r') as vlt:
				crypt = vlt.read()
		except FileNotFoundError:
			return None
		return load(str(self.decrypt(crypt)))

	def _writecrypt(self, plain):
		"""crypt file writing method"""
		if self.dbg:
			print(bgre(tabd({self._writecrypt: {'plain': plain}})))
		kwargs = {'output': self.crypt}
		if self.recvs:
			kwargs['recipients'] = self.recvs
		self.__weaks = plain
		try:
			copyfile(self.crypt, '%s.1'%self.crypt)
			chmod('%s.1'%self.crypt, 0o600)
		except FileNotFoundError:
			pass
		while True:
			self.encrypt(message=dump(self.__weaks), **kwargs)
			if self._chkcrypt():
				if self.remote:
					self._copynews_()
				chmod(self.crypt, 0o600)
				break
		return True

	def adpw(self, usr, pwd=None):
		"""password adding method"""
		if self.dbg:
			print(bgre(tabd({
                self.adpw: {'user': self.user, 'entry': usr, 'pwd': pwd}})))
		pwdcom = [pwd if pwd else self._passwd()]
		com = input('enter a comment: ')
		if com:
			pwdcom.append(com)
		if self.dbg:
			print('%s\n adduser = %s addpass = %s'%(
                self.adpw, usr, pwd))
		__weak = self._readcrypt()
		if __weak and self.user in __weak.keys():
			__weak[self.user][usr] = pwdcom
			self._writecrypt(__weak)
			return True

	def chpw(self, usr, pwd=None):
		"""change existing password method"""
		if self.dbg:
			print(bgre(tabd({
                self.chpw: {'user': self.user, 'entry': usr, 'pwd': pwd}})))
		pwdcom = [pwd if pwd else self._passwd()]
		com = input('enter a comment: ')
		if com:
			pwdcom.append(com)
		if self.dbg:
			print('%s\n adduser = %s addpass, comment = %s'%(
                self.chpw, usr, pwdcom))
		__weak = self._readcrypt()
		if __weak and self.user in __weak.keys() and \
              usr in __weak[self.user].keys():
			__weak[self.user][usr] = pwdcom
			self._writecrypt(__weak)
			return True

	def rmpw(self, usr):
		"""remove password method"""
		if self.dbg:
			print(bgre(tabd({self.rmpw: {'user': self.user, 'entry': usr}})))
		__weak = self._readcrypt()
		if __weak and self.user in __weak.keys() and \
              usr in __weak[self.user].keys():
			del __weak[self.user][usr]
			if self._writecrypt(__weak):
				if self.remote:
					self._copynews_()
			return True

	def lspw(self, usr=None, aal=None):
		"""password listing method"""
		if self.dbg:
			print(bgre(tabd({self.lspw: {'user': self.user, 'entry': usr}})))
		aal = True if aal else self.aal
		if self.__weaks:
			if aal:
				__ents = self.__weaks
				if usr:
					for (user, _) in self.__weaks.items():
						__match = self._findentry(usr, self.__weaks[user])
						if __match:
							__ents = {usr: __match}
							break
			elif self.user in self.__weaks.keys():
				__ents = self.__weaks[self.user]
				if usr:
					__ents = {usr: self._findentry(usr, __ents)}
			return __ents

def lscrypt(usr, dbg=None):
	"""passlist wrapper function"""
	if dbg:
		print(bgre(lscrypt))
	if usr:
		return PassCrypt().lspw(usr)




if __name__ == '__main__':
	exit(1)
