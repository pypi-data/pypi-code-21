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
Instance module.
"""

class Instance:

	"""
	Instance.

	:param caviar.domain.ManagedDomainContext context:
	   Managed domain context.
	:param str name:
	   Instance name.
	:param caviar.domain.cluster.Cluster cluster:
	   Cluster where instance participates.
	:param caviar.domain.node.Node node:
	   Node where instance resides.
	:param str ajp_port:
	   AJP 1.3 port.
	"""

	def __init__(self, context, name, node, ajp_port):

		self.__context = context
		self.__name = name
		self.__node = node
		self.__ajp_port = ajp_port
		
	def __eq__(self, other):

		return self.__name == other.__name
		
	@property
	def name(self):
	
		"""
		Instance name.
		
		:rtype:
		   str
		"""
		
		return self.__name
		
	@property
	def host(self):
	
		"""
		Instance host.
		
		:rtype:
		   str
		"""
		
		return self.__node.host
		
	@property
	def ajp_port(self):
	
		"""
		AJP 1.3 port.
		
		:rtype:
		   str
		"""
		
		return self.__ajp_port
		
def restore(context, name, node, resource):

	config_ref = resource.extra_properties.entity.configRef
	res = context.management().domain()
	res = res.extra_properties.child_resources["configs"]
	res = res.extra_properties.child_resources["config"]
	res = res.extra_properties.child_resources[config_ref]
	res = res.raise_not_success()
	res = res.extra_properties.child_resources["network-config"]
	res = res.extra_properties.child_resources["network-listeners"]
	res = res.extra_properties.child_resources["network-listener"]
	res = res.extra_properties.child_resources["http-listener-1"]
	res = res.raise_not_success()
	return Instance(
		context,
		name,
		node,
		res.extra_properties.entity.port
	)

