#!/usr/bin/env python3
"""ssh connection and remote command """

#global imports"""
import os
import sys
from shutil import copy2
from socket import \
    gaierror as NameResolveError, timeout as sockettimeout
from paramiko import ssh_exception, SSHClient, AutoAddPolicy, SSHException

from colortext import bgre, tabd, abort, error
from system import whoami
from net import askdns

# default vars
__version__ = '0.1'

class SecureSHell(object):
	"""paramiko wrapper class"""
	dbg = None
	reuser = ''
	remote = ''
	def __init__(self, *args, **kwargs):
		"""ssh init function"""
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if self.dbg:
			print(bgre(SecureSHell.__mro__))
			print(bgre(tabd(self.__dict__, 2)))

	def _ssh_(self, remote, reuser=None, port=22):
		"""ssh connector method"""
		if '@' in remote:
			reuser, remote = remote.split('@')
		reuser = whoami() if not reuser else reuser
		if self.dbg:
			print(bgre('%s\n  remote = %s\n  reuser = %s\n  port = %d'%(
                self._ssh_, remote, reuser, port)))
		ssh = SSHClient()
		ssh.set_missing_host_key_policy(AutoAddPolicy())
		try:
			ssh.connect(
                askdns(remote), int(port),
                username=reuser, allow_agent=True, look_for_keys=True)
		except (ssh_exception.SSHException, NameResolveError) as err:
			error(self._ssh_, err)
			raise err
		return ssh

	def rrun(self, cmd, remote=None, reuser=None):
		"""remote run method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rrun, err)
			raise err

	def rcall(self, cmd, remote=None, reuser=None):
		"""remote call method"""
		remote = remote if remote else self.remote
		reuser = reuser if reuser else self.reuser
		#print(remote)
		#print(reuser)
		if self.dbg:
			print(bgre(self.rcall))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			chn = ssh.get_transport().open_session()
			chn.settimeout(10800)
			chn.exec_command(cmd)
			while not chn.exit_status_ready():
				if chn.recv_ready():
					och = chn.recv(1024)
					while och:
						sys.stdout.write(och.decode())
						och = chn.recv(1024)
				if chn.recv_stderr_ready():
					ech = chn.recv_stderr(1024)
					while ech:
						sys.stderr.write(ech.decode())
						ech = chn.recv_stderr(1024)
			return int(chn.recv_exit_status())
		except (
            AttributeError, ssh_exception.SSHException, sockettimeout
            ) as err:
			error(self.rcall, err)
			raise err
		except KeyboardInterrupt:
			abort()

	def rstdx(self, cmd, remote=None, reuser=None):
		"""remote stout/error method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			_, out, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstdx, err)
			raise err
		return ''.join(out.readlines()), ''.join(err.readlines())


	def rstdo(self, cmd, remote=None, reuser=None):
		"""remote stdout method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			_, out, _ = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstdo, err)
			raise err
		return ''.join(out.readlines())

	def rstde(self, cmd, remote=None, reuser=None):
		"""remote stderr method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			_, _, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstde, err)
			raise err
		return ''.join(err.readlines())

	def rerno(self, cmd, remote=None, reuser=None):
		"""remote error code  method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rerno))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			_, out, _ = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rerno, err)
			raise err
		return int(out.channel.recv_exit_status())

	def roerc(self, cmd, remote=None, reuser=None):
		"""remote stdout/stderr/errorcode method"""
		remote = remote if remote else self.remote
		#print(remote)
		reuser = reuser if reuser else self.reuser
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s %s %s'%(reuser, remote, cmd)))
		ssh = self._ssh_(remote, reuser)
		try:
			_, out, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.roerc, err)
			raise err
		return ''.join(out.readlines()), ''.join(err.readlines()), \
            out.channel.recv_exit_status()

	def get(self, src, trg, remote=None, reuser=None):
		"""sftp get method"""
		if self.dbg:
			print(bgre(self.get))
		reuser = reuser if reuser else self.reuser
		remote = remote if remote else self.remote
		if not (os.path.isfile(src) or os.path.isfile(trg)):
			raise FileNotFoundError('connot find either %s nor %s'%(src, trg))
		ssh = self._ssh_(remote, reuser)
		scp = ssh.open_sftp()
		return scp.get(src, trg)

	def put(self, src, trg, remote=None, reuser=None):
		"""sftp put method"""
		if self.dbg:
			print(bgre(self.put))
		reuser = reuser if reuser else self.reuser
		remote = remote if remote else self.remote
		if not (os.path.isfile(src) or os.path.isfile(trg)):
			raise FileNotFoundError('connot find either %s nor %s'%(src, trg))
		ssh = self._ssh_(remote, reuser)
		scp = ssh.open_sftp()
		return scp.put(src, trg)

	def rcompstats(self, src, trg, remote=None, reuser=None):
		"""remote file-stats compare """
		if self.dbg:
			print(bgre(self.rcompstats))
		remote = remote if remote else self.remote
		reuser = reuser if reuser else self.reuser
		smt = int(str(int(os.stat(src).st_mtime))[:6])
		rmt = self.rstdo(
            'stat -c %%Y %s'%trg, remote=remote, reuser=reuser)
		if rmt:
			rmt = int(str(rmt)[:6])
		if rmt == smt:
			return
		srctrg = src, '%s@%s:%s'%(reuser, remote, trg)
		if rmt and int(rmt) > int(smt):
			srctrg = '%s@%s:%s'%(reuser, remote, trg), src
		return srctrg

	def _localstamp(self, trg):
		"""local file-timestamp method"""
		if self.dbg:
			print(bgre(self._localstamp))
		return int(os.stat(trg).st_atime), int(os.stat(trg).st_mtime)

	def _remotestamp(self, trg, remote, reuser):
		"""remote file-timestamp method"""
		if self.dbg:
			print(bgre(self._remotestamp))
		tat = self.rstdo(
            'stat -c %%X %s'%trg, remote, reuser).strip()
		tmt = self.rstdo(
            'stat -c %%Y %s'%trg, remote, reuser).strip()
		#print(tat)
		if tat and tmt: return int(tat), int(tmt)
		return None, None

	def _setlstamp(self, trg, atime, mtime):
		"""local file-timestamp set method"""
		if self.dbg:
			print(bgre(self._setlstamp))
		os.utime(trg, (atime, mtime))

	def _setrstamp(self, trg, atime, mtime, remote, reuser):
		"""remote file-timestamp set method"""
		if self.dbg:
			print(bgre(self._setrstamp))
		self.rstdo(
            'touch -a --date=@%s %s'%(atime, trg), remote, reuser)
		self.rstdo(
            'touch -m --date=@%s %s'%(mtime, trg), remote, reuser)

	def scpcompstats(self, lfile, rfile, remote=None, reuser=None):
		"""
		remote/local file compare method copying and
		setting the file/timestamp of the neweer one
		"""
		if self.dbg:
			print(bgre(self.scpcompstats))
		reuser = reuser if reuser else self.reuser
		remote = remote if remote else self.remote
		try:
			lat, lmt = self._localstamp(lfile)
			rat, rmt = self._remotestamp(rfile, remote, reuser)
			if rmt == lmt:
				return
			elif rmt and rmt > lmt:
				copy2(lfile, '%s.1'%lfile)
				self.get(rfile, lfile, remote, reuser)
				self._setlstamp(lfile, rat, rmt)
			else:
				self.put(lfile, rfile, remote, reuser)
				self._setlstamp(rfile, lat, lmt)
		except SSHException as err:
			error(err)
		return True



if __name__ == '__main__':
	"""module debugging area"""
	#ssh = SecureSHell(**{'remote':'bigbox.janeiskla.de'})
	#print(ssh.command('cat /etc/debian_version'))
