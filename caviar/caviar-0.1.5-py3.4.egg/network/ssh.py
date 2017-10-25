#
# This file is part of CAVIAR.
#
# CAVIAR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CAVIAR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CAVIAR.  If not, see <http://www.gnu.org/licenses/>.
#

"""
SSH module.
"""

import importlib
import time

class SSHUnavailableSessionError(BaseException):

	def __init__(self, target):
	
		super().__init__([
			target
		])
		self.__target = target
		
	@property
	def target(self):
	
		return self.__target
		
class SSHInvalidSessionError(BaseException):

	def __init__(self, target):
	
		super().__init__([
			target
		])
		self.__target = target
		
	@property
	def target(self):
	
		return self.__target
			
class SSHCommandError(BaseException):

	def __init__(self, target, cause_lines):
	
		super().__init__([
			target,
			cause_lines
		])
		self.__target = target
		self.__cause_lines = cause_lines
		
	@property
	def target(self):
	
		return self.__target
		
	@property
	def cause_lines(self):
	
		return self.__cause_lines
		
class SSHSessionFactory:

	"""
	SSH session factory.
	"""

	def __init__(self, ssh_client, private_key_path):

		self.__pool = SSHSessionPool(ssh_client, private_key_path)
		
	def session(self, user, host, attempt_count=5, attempt_timeout=1):
	
		return SSHSession(
			self.__pool,
			SSHUserHost(user, host),
			attempt_count,
			attempt_timeout
		)
		
	def close(self):
	
		self.__pool.close()
		
class SSHSession:

	"""
	SSH logic session.
	
	:param SSHSessionPool pool:
	   Session pool.
	:param SSHUserHost target:
	   Session target.
	:param int attempt_count:
	   Session availability attempt count.
	:param int attempt_timeout:
	   Session availability attempt timeout.
	"""
	
	def __init__(self, pool, target, attempt_count, attempt_timeout):
	
		if attempt_count < 1:
			raise ValueError("Bad attempt count: {}".format(attempt_count))
			
		self.__pool = pool
		self.__target = target
		self.__physical_session = None
		self.__attempt_count = attempt_count
		self.__attempt_timeout = attempt_timeout
		
	def __execute(self, cmd):
	
		stdout, stderr = self.__pool.get(self.__target).execute(cmd)
		
		cause_lines = []
		line = stderr.readline()
		while len(line) > 0:
			cause_lines.append(line.strip())
			line = stderr.readline()
		if len(cause_lines) > 0:
			raise SSHCommandError(self.__target, cause_lines)
			
		line = stdout.readline()
		while len(line) > 0:
			yield line.strip()
			line = stdout.readline()
			
	def __retry(self, available_attempts):
	
		new_available_attempts = available_attempts - 1
		if new_available_attempts < 1:
			raise SSHUnavailableSessionError(self.__target)
		time.sleep(self.__attempt_timeout)
		return new_available_attempts
		
	def execute(self, cmd):
	
		"""
		Execute the specified command.
		
		:param str cmd:
		   Command to be executed.
		   
		:rtype:
		   iter
		:return:
		   Iterator of standard output lines.
		   
		:raise caviar.network.ssh.SSHUnavailableSessionError:
		   If it is not possible to use any physical session.
		:raise caviar.network.ssh.SSHCommandError:
		   If there was a command error.
		"""
		
		should_continue = True
		available_attempts = self.__attempt_count
		while should_continue:
			try:
				yield from self.__execute(cmd)
				should_continue = False
			except SSHUnavailableSessionError:
				available_attempts = self.__retry(available_attempts)
			except SSHInvalidSessionError:
				self.__pool.discard(self.__target)
				available_attempts = self.__retry(available_attempts)
				
class SSHSessionPool:

	def __init__(self, ssh_client, private_key_path):
	
		self.__ssh_client = ssh_client
		self.__private_key_path = private_key_path
		self.__physical_sessions = {}
		
	def get(self, target):
	
		try:
			return self.__physical_sessions[target]
		except KeyError:
			physical_session = self.__ssh_client.login(
				target,
				self.__private_key_path
			)
			self.__physical_sessions[target] = physical_session
			return physical_session
		
	def discard(self, target):
	
		del self.__physical_sessions[target]
			
	def close(self):
	
		self.__ssh_client.close()
		for target, physical_session in self.__physical_sessions.items():
			physical_session.logout()
		self.__physical_sessions.clear()
		
class SSHUserHost:

	def __init__(self, user, host):
	
		self.__user = user
		self.__host = host
		
	@property
	def user(self):
	
		return self.__user
		
	@property
	def host(self):
	
		return self.__host
		
	def __hash__(self):
	
		return hash((self.__user, self.__host))
		
	def __eq__(self, other):
	
		return self.__user == other.user and self.__host == other.host
		
	def __ne__(self, other):
	
		return self.__user != other.user or self.__host != other.host
		
	def __repr__(self):
	
		return "{}@{}".format(self.__user, self.__host)

