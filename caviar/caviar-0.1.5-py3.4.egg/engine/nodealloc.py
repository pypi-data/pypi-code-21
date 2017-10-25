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
Node allocator module.
"""

class NodeAllocator:

	"""
	Node allocator.
	"""

	def __init__(self, ssh_session_fact, das_machine, node_alloc_machine):

		self.__das_machine = das_machine
		self.__node_alloc_machine = node_alloc_machine
		
		self.__das_ssh_session = ssh_session_fact.session(
			das_machine.appserver_user,
			das_machine.host
		)
		self.__node_alloc_ssh_session = ssh_session_fact.session(
			node_alloc_machine.appserver_user,
			node_alloc_machine.host
		)
		
	def prepare(self, domain_name, node_name):
	
		"""
		Install the specified domain saved master password to the specified node
		file system.

		:param str domain_name:
		   Name of the domain who owns the saved master password.
		:param str node_name:
		   Name of the node where the master password must be installed on.
		   
		:rtype:
		   str
		:return:
		   The node allocator host.
		"""
		
		any(self.__node_alloc_ssh_session.execute(
			self.__node_alloc_machine.ping_cmd()
		))
		any(self.__das_ssh_session.execute(
			self.__das_machine.install_master_password_cmd(
				domain_name,
				node_name,
				self.__node_alloc_machine.host
			)
		))
		return self.__node_alloc_machine.host

