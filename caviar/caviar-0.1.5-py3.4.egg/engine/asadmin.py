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
Asadmin module.
"""

import random
import string

class Asadmin:

	"""
	Asadmin utility.
	"""

	def __init__(self, ssh_session_fact, das_machine, master_password):

		self.__ssh_session = ssh_session_fact.session(
			das_machine.appserver_user,
			das_machine.host
		)
		self.__das_machine = das_machine
		self.__master_password = master_password
		
	def __create_pwd_id(self):
	
		return "".join(
			random.choice(string.ascii_lowercase + string.digits)
			for _ in range(8)
		)
		
	def __run(self, cmd, host=None, port=None, user=None, passwords=None,
			params=None):
			
		try:
		
			args = []
			args.extend([ "--terse", "true" ])
			args.extend([ "--echo", "false" ])
			args.extend([ "--interactive", "false" ])
			
			if host is not None:
				args.extend([ "--host", host ])
			if port is not None:
				args.extend([ "--port", port ])
			if user is not None:
				args.extend([ "--user", user ])
				
			pwd_id = None
			if passwords is not None:
				pwd_id = self.__create_pwd_id()
				any(self.__ssh_session.execute(
					self.__das_machine.create_password_file_cmd(
						pwd_id,
						passwords
					)
				))
				args.extend([
					"--passwordfile",
					self.__das_machine.password_file_path(pwd_id)
				])
				
			args.append(cmd)
			if params is not None:
				args.extend(params)
				
			yield from self.__ssh_session.execute(
				self.__das_machine.asadmin_cmd(args)
			)
			
		finally:
		
			if pwd_id is not None:
				any(self.__ssh_session.execute(
					self.__das_machine.delete_password_file_cmd(pwd_id)
				))
					
	def list_domains(self):
	
		params = []
		params.append("--long")
		params.extend([ "--header", "false" ])
		for line in self.__run(cmd="list-domains", params=params):
			values = line.split()
			yield {
				"name": values[0],
				"admin-host": values[1],
				"admin-port": values[2],
				"running": values[3] == "true",
				"restart-required": values[4] == "true"
			}
			
	def create_domain(self, name, admin_user, admin_password):
	
		params = []
		params.extend([ "--usemasterpassword", "true" ])
		params.extend([ "--savemasterpassword", "true" ])
		params.append(name)
		any(self.__run(
			cmd="create-domain",
			params=params,
			host=self.__das_machine.host,
			user=admin_user,
			passwords={
				"AS_ADMIN_MASTERPASSWORD": self.__master_password,
				"AS_ADMIN_PASSWORD": admin_password
		}))
		
	def enable_secure_admin(self, admin_port, admin_user, admin_password):
	
		any(self.__run(
			cmd="enable-secure-admin",
			host=self.__das_machine.host,
			port=admin_port,
			user=admin_user,
			passwords={
				"AS_ADMIN_PASSWORD": admin_password
		}))
		
	def set_admin_listener_host(self, admin_port, admin_user, admin_password):
	
		params = []
		params.append(
			"configs.config.server-config.network-config.network-listeners."
			"network-listener.admin-listener.address={}".format(
				self.__das_machine.host
			)
		)
		any(self.__run(
			cmd="set",
			params=params,
			host=self.__das_machine.host,
			port=admin_port,
			user=admin_user,
			passwords={
				"AS_ADMIN_PASSWORD": admin_password
		}))
		
	def start_domain(self, name):
	
		params = []
		params.append(name)
		any(self.__run(
			cmd="start-domain",
			params=params,
			passwords={
				"AS_ADMIN_MASTERPASSWORD": self.__master_password
		}))
		
	def stop_domain(self, name):
	
		params = []
		params.append(name)
		any(self.__run(
			cmd="stop-domain",
			params=params,
			passwords={
				"AS_ADMIN_MASTERPASSWORD": self.__master_password
		}))

