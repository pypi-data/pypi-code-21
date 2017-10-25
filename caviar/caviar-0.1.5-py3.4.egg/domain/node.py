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
Node module.
"""

import caviar
import caviar.domain
import caviar.domain.instance

class Node:

	"""
	Node.

	:param caviar.domain.ManagedDomainContext context:
	   Managed domain context.
	:param str name:
	   Node name.
	:param str host:
	   Node host.
	"""

	def __init__(self, context, name, host):

		self.__context = context
		self.__name = name
		self.__host = host
		
	def __hash__(self):
	
		return hash(self.__name)
		
	def __eq__(self, other):

		return self.__name == other.__name
		
	def __str__(self):
	
		return self.__name
		
	def __management(self):

		return self.__context.management()
		
	def __load_balancer(self, name):

		return self.__context.load_balancer(cluster)
		
	@property
	def name(self):
	
		"""
		Node name.
		
		:rtype:
		   str
		"""
		
		return self.__name
		
	@property
	def host(self):
	
		"""
		Node host.
		
		:rtype:
		   str
		"""
		
		return self.__host
		
	def instances(self):

		"""
		Node instances.

		:rtype:
		   iter
		:return:
		   Iterator that yields node instances.
		"""
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["servers"]
		res = res.extra_properties.child_resources["server"]
		for name, inst_res in res.extra_properties.child_resources.items():
			if inst_res.extra_properties.entity.nodeRef == self.__name:
				yield caviar.domain.instance.restore(
					self.__context,
					name,
					self,
					inst_res
				)
				
	def create_instance(self, name, cluster):
	
		"""
		Create a new noide instance for participating in the given cluster.
		
		:param str name:
		   Instance name.
		:param caviar.domain.cluster.Cluster cluster:
		   Cluster where participate in.
		   
		:rtype:
		   caviar.domain.instance.Instance
		:return:
		   The created instance.
		"""
		
		res = self.__management().domain()
		res.extra_properties.commands.create_instance(
			id=name,
			nodeagent=self.__name,
			cluster=cluster.name
		)
		
		res = self.__management().domain()
		res = res.extra_properties.child_resources["servers"]
		res = res.extra_properties.child_resources["server"]
		res.extra_properties.child_resources.cache_evict()
		created_instance = next(
			filter(
				lambda inst: inst.name == name,
				self.instances()
			),
			None
		)
		# TODO Enable load balancer...
		#	self.__load_balancer(cluster.name).add_instance(
		#		created_instance.name,
		#		created_instance.host,
		#		created_instance.ajp_port
		#	)
		return created_instance
		
def restore(context, name, resource):

	return Node(
		context,
		name,
		resource.extra_properties.entity.nodeHost
	)

