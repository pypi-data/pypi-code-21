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
Engine module.
"""

import caviar.engine.asadmin
import caviar.engine.lb
import caviar.engine.management
import caviar.engine.nodealloc
import caviar.network

class Engine:

	"""
	GlassFish engine.

	:param Machinery machinery:
	   Provided machinery.
	:param ssh.SSHSessionFactory ssh_session_fact:
	   SSH session factory.
	:param str master_password:
	   Used master password.
	"""

	def __init__(self, machinery, ssh_session_fact, master_password,
			das_server_name, node_alloc_server_prefix):

		self.__machinery = machinery
		self.__ssh_session_fact = ssh_session_fact
		self.__master_password = master_password
		self.__das_server_name = das_server_name
		self.__node_alloc_server_prefix = node_alloc_server_prefix

	def __das_machine(self):
	
		return self.__machinery.server(self.__das_server_name)
		
	def __node_allocator_machine(self, name):
	
		return self.__machinery.server("{}-{}".format(
			self.__node_alloc_server_prefix,
			name
		), [
			self.__das_machine().appserver_public_key_path
		])
		
	def __load_balancer_machine(self, name):
	
		return self.__machinery.load_balancer(name)
		
	# TODO Test coverage
	@property
	def server_node_dir(self):
	
		"""
		Server node directory.
		
		:rtype:
		   str
		"""
		
		return self.__machinery.server_node_dir
		
	def management(self, domain_name, admin_port, admin_user, admin_password):

		"""
		DAS management client.
		   
		:rtype:
		   management.Management
		:return:
		   The DAS management client.
		"""

		return caviar.engine.management.Management(
			self.__das_machine(),
			admin_port,
			caviar.network.http.HTTPBasicAuth(
				admin_user,
				admin_password
			)
		)

	def asadmin(self):

		"""
		DAS `asadmin` utility.

		:rtype:
		   asadmin.Asadmin
		:return:
		   The DAS `asadmin` utility.
		"""

		return caviar.engine.asadmin.Asadmin(
			self.__ssh_session_fact,
			self.__das_machine(),
			self.__master_password
		)

	def node_allocator(self, name):
	
		"""
		Restore the node allocator with the given name and make it manageable.
		
		:param str name:
		   Node allocator name.
		   
		:rtype:
		   nodealloc.NodeAllocator
		:return:
		   The node allocator.
		"""
		
		return caviar.engine.nodealloc.NodeAllocator(
			self.__ssh_session_fact,
			self.__das_machine(),
			self.__node_allocator_machine(name)
		)
		
	def load_balancer(self, cluster_name):
	
		"""
		Restore the load balance machine for the specified cluster and make it
		manageable.
		
		:param str cluster_name:
		   Name of the cluster which load will be balanced.
		
		:rtype:
		   lb.LoadBalancer
		:return:
		   The load balancer.
		"""
		
		return caviar.engine.lb.LoadBalancer(
			self.__ssh_session_fact,
			self.__load_balancer_machine(cluster_name)
		)
		
	def close(self):
	
		"""
		Close this engine.
		
		Log out from all SSH sessions.
		"""
		
		self.__ssh_session_fact.close()

