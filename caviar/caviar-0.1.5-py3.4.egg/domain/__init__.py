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
Domain module.
"""

import caviar.domain.cluster
import caviar.domain.node
import caviar.engine
import caviar.network

import importlib
import sys

class Domain:

	"""
	Domain.

	:param caviar.engine.Engine engine:
	   Underlying engine.
	"""

	def __init__(self, engine, name, admin_host, admin_port, running,
			restart_required):

		self.__engine = engine
		self.__name = name
		self.__admin_host = admin_host
		self.__admin_port = admin_port
		self.__running = running
		self.__restart_required = restart_required

	def __eq__(self, other):

		return self.__name == other.__name

	def __asadmin(self):

		return self.__engine.asadmin()

	@property
	def name(self):
	
		"""
		Domain name.
		
		:rtype:
		   str
		"""
		
		return self.__name
		
	@property
	def admin_port(self):
	
		"""
		Administrator port.
		
		:rtype:
		   str
		"""
		
		return self.__admin_port
		
	def manage(self, admin_user, admin_password):

		"""
		Manage this domain.

		Ensure it is running and without requiring to be restarted, and update
		its state.

		:param str admin_user:
			Name of the administrator user.
		:param str admin_password:
			Password of the administrator user.

		:rtype:
			ManagedDomain
		:return:
			The managed domain.
		"""

		asadmin = self.__asadmin()
		if not self.__running:
			asadmin.start_domain(self.__name)
		elif self.__restart_required:
			asadmin.restart_domain(self.__name)
		self.__running = True
		self.__restart_required = False
		
		return ManagedDomain(ManagedDomainContext(
			self.__engine,
			self.__name,
			self.__admin_port,
			admin_user,
			admin_password
		))

class ManagedDomain:

	"""
	Managed domain.

	:param ManagedDomainContext context:
	   Managed domain context.
	"""

	def __init__(self, context):
	
		self.__context = context
		
	def __management(self):

		return self.__context.management()
		
	def __prepare_node(self, allocator_name, name):

		return self.__context.prepare_node(allocator_name, name)
		
	def nodes(self):

		"""
		Available nodes.

		:rtype:
		   iter
		:return:
		   Iterator that yields available nodes.
		"""
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["nodes"]
		res = res.extra_properties.child_resources["node"]
		for name, node_res in res.extra_properties.child_resources.items():
			if node_res.extra_properties.entity.type == "SSH":
				yield caviar.domain.node.restore(
					self.__context,
					name,
					node_res
				)
				
	def create_node(self, name, allocator_name):

		"""
		Create a node on this domain.

		:param str name:
		   Node name.
		:param str allocator_name:
			Node allocator name.

		:rtype:
		   node.Node
		:return:
		   The created node.
		"""
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["nodes"]
		res.extra_properties.commands.create_node_ssh(
			id=name,
			install=False,
			nodedir=self.__context.node_dir,
			nodehost=self.__prepare_node(allocator_name, name)
		)
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["nodes"]
		res = res.extra_properties.child_resources["node"]
		res.extra_properties.child_resources.cache_evict()
		return next(
			filter(
				lambda node: node.name == name,
				self.nodes()
			),
			None
		)
		
	def clusters(self):

		"""
		Available clusters.

		:rtype:
		   iter
		:return:
		   Iterator that yields available clusters.
		"""
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["clusters"]
		res = res.extra_properties.child_resources["cluster"]
		for name, cluster_res in res.extra_properties.child_resources.items():
			yield caviar.domain.cluster.restore(
				self.__context,
				name,
				cluster_res
			)
			
	def create_cluster(self, name):
			
		res = self.__management().domain()
		res = res.extra_properties.child_resources["clusters"]
		res = res.extra_properties.child_resources["cluster"]
		res = res.extra_properties.methods.post(
			id=name
		)
		res.extra_properties.child_resources.cache_evict()
		return next(
			filter(
				lambda clust: clust.name == name,
				self.clusters()
			),
			None
		)
		
class ManagedDomainContext:

	"""
	Managed domain context.
	
	:param caviar.engine.Engine engine:
	   Underlying engine.
	:param str domain_name:
	   Domain name.
	:param str admin_port:
	   Administrator port.
	:param str admin_user:
	   Administrator user name.
	:param str admin_password:
	   Administrator password.
	"""
	
	def __init__(self, engine, domain_name, admin_port, admin_user,
			admin_password):
			
		self.__engine = engine
		self.__domain_name = domain_name
		self.__admin_port = admin_port
		self.__admin_user = admin_user
		self.__admin_password = admin_password
		
	def __node_allocator(self, name):
	
		return self.__engine.node_allocator(name)
		
	# TODO Test coverage
	@property
	def node_dir(self):
	
		"""
		Node directory.
		
		:rtype:
		   str
		"""
		
		return self.__engine.server_node_dir
		
	def management(self):
	
		"""
		Domain management for this context.
		
		:rtype:
		   caviar.engine.management.Management
		:return:
		   Domain management.
		"""
		
		return self.__engine.management(
			self.__domain_name,
			self.__admin_port,
			self.__admin_user,
			self.__admin_password
		)
		
	def prepare_node(self, allocator_name, name):
		
		"""
		Prepare an allocated node.
		
		:param str allocator_name:
		   Node allocator name.
		:param str name:
		   Node name.
		   
		:rtype:
		   str
		:return:
		   Node allocator host.
		"""
		
		return self.__node_allocator(allocator_name).prepare(
			self.__domain_name,
			name
		)
		
class Environment:

	"""
	GlassFish environment.

	:param caviar.engine.Engine engine:
	   GlassFish engine.
	"""

	def __init__(self, engine):

		self.__engine = engine

	def __asadmin(self):

		return self.__engine.asadmin()
		
	def domains(self):

		"""
		Available domains.

		:rtype:
		   iter
		:return:
		   Iterator that yields available domains.
		"""

		for data in self.__asadmin().list_domains():
			yield Domain(
				self.__engine,
				data["name"],
				data["admin-host"],
				data["admin-port"],
				data["running"],
				data["restart-required"]
			)
			
	def create_domain(self, name, admin_user, admin_password):
	
		"""
		Create a domain.
		
		:param str name:
		   Domain name.
		:param str admin_user:
		   Administrator user name.
		:param str admin_password:
		   Administrator user password.
		   
		:rtype:
		   Domain
		:return:
		   The created domain.
		"""
		
		self.__asadmin().create_domain(
			name,
			admin_user,
			admin_password
		)
		created_domain = next(
			filter(
				lambda domain: domain.name == name,
				self.domains()
			),
			None
		)
		self.__asadmin().start_domain(
			created_domain.name
		)
		self.__asadmin().enable_secure_admin(
			created_domain.admin_port,
			admin_user,
			admin_password
		)
		self.__asadmin().set_admin_listener_host(
			created_domain.admin_port,
			admin_user,
			admin_password
		)
		self.__asadmin().stop_domain(
			created_domain.name
		)
		return next(
			filter(
				lambda domain: domain.name == name,
				self.domains()
			),
			None
		)
		
	def close(self):
	
		"""
		Close this environment.
		
		Shutdown the engine.
		"""
		
		self.__engine.close()
		
def environment(
	machinery_module_name,
	machinery_params,
	mgmt_public_key_path,
	mgmt_private_key_path,
	master_password,
	log_out=sys.stdout,
	ssh_module_name="caviar.provider.ssh.paramiko",
	das_server_name="das",
	node_alloc_server_prefix="nodealloc"
):

	"""
	Restore the specified environment.

	:param str machinery_module_name:
	   Machinery module name.
	:param dict machinery_params:
	   Machinery parameters.
	:param str mgmt_public_key_path:
	   Management public key path.
	:param str mgmt_private_key_path:
	   Management private key path.
	:param str master_password:
	   Used master password.
	:param fileobj log_out:
	   Logging output.

	:rtype:
	   Environment
	:return:
	   The restored environment.
	"""

	machinery_module = importlib.import_module(machinery_module_name)
	ssh_module = importlib.import_module(ssh_module_name)
	return Environment(caviar.engine.Engine(
		machinery_module.Machinery(
			machinery_params,
			mgmt_public_key_path,
			log_out
		),
		caviar.network.ssh_session_factory(
			ssh_module.SSHClient(),
			mgmt_private_key_path
		),
		master_password,
		das_server_name,
		node_alloc_server_prefix
	))
