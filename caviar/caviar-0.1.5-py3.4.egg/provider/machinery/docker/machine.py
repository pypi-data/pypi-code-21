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

class Machine:

	def __init__(self, client, container_id):
	
		self.__client = client
		self.__container_id = container_id
		self.__cached_info = None
		
	@property
	def __info(self):
	
		if self.__cached_info is None:
			self.__cached_info = MachineInfo(
				self.__client,
				self.__container_id
			)
		return self.__cached_info
		
	@property
	def host(self):
	
		return self.__info.host
		
	# TODO Test coverage
	def ping_cmd(self):
	
		return "echo"
		
class MachineInfo:

	def __init__(self, client, container_id):
	
		cont_list = client.containers(all=True, filters={
			"id": container_id
		})
		cont = cont_list[0]
		if cont["State"] != "running":
			client.start(container=container_id)
			
		cont_list = client.containers(all=True, filters={
			"id": container_id
		})
		cont = cont_list[0]
		
		bridge_network = cont["NetworkSettings"]["Networks"]["bridge"]
		self.__host = bridge_network["IPAddress"]
		
	@property
	def host(self):
	
		return self.__host

