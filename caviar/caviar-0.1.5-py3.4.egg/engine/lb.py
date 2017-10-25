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
Load balancer module.
"""

class LoadBalancer:

	"""
	Load balancer.
	"""

	def __init__(self, ssh_session_fact, lb_machine):

		self.__ssh_session = ssh_session_fact.session(
			lb_machine.web_user,
			lb_machine.host
		)
		self.__lb_machine = lb_machine
		
	def add_instance(self, name, host, port):

		"""
		Add an instance with the given name, host and port to the load balancer.

		:param str name:
		   Instance name.
		:param str host:
		   Instance host.
		:param str port:
		   Instance port.
		"""

		for line in self.__ssh_session.execute(
			self.__lb_machine.add_instance_cmd(name, host, port)
		):
			pass

	def remove_instance(self, name):

		"""
		Remove the instance with the given name from the load balancer.
		
		:param str name:
		   Instance name.
		"""

		for line in self.__ssh_session.execute(
			self.__lb_machine.remove_instance_cmd(name)
		):
			pass

