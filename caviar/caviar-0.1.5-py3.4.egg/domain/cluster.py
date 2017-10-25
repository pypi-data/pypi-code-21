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
Cluster module.
"""

import caviar.domain.instance

class Cluster:

	"""
	Cluster.

	:param caviar.domain.ManagedDomainContext context:
	   Managed domain context.
	:param str name:
	   Cluster name.
	"""

	def __init__(self, context, name):

		self.__context = context
		self.__name = name
		
	def __eq__(self, other):

		return self.__name == other.__name
			
	@property
	def name(self):
	
		"""
		Node name.
		
		:rtype:
		   str
		"""
		
		return self.__name
		
def restore(context, name, resource):

	return Cluster(
		context,
		name
	)

