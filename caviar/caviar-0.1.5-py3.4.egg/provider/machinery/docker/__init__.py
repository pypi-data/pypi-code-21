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

import os

import caviar

class Machinery:

	def __init__(self, params, mgmt_public_key_path, log_out):
	
		self.__APPSERVER_USER = "glassfish"
		self.__WEB_USER = "apache"
		
		self.__IMAGE_TAG = "latest"
		self.__BRANCH_NAME = "master"
		
		self.__client = params["client"]
		self.__base_name_str = "{}-".format(params["base-name"]) \
			if "base-name" in params \
			else ""
		self.__mgmt_public_key_path = mgmt_public_key_path
		self.__log_out = log_out
		
		if "build-images" in params and params["build-images"]:
			self.__build_image("debian")
			self.__build_image("server")
			
	def __build_image(self, image_type):
	
		for line in self.__client.build(
			path=self.__github_url(image_type),
			tag=self.__image_name(image_type),
			rm=True
		):
			line_dict = eval(line.decode("UTF-8"))
			if "stream" in line_dict:
				self.__log_out.write(line_dict["stream"])
				
	def __github_url(self, image_type):
	
		return "https://github.com/miquelo" \
				"/docker-glassfish.git#{}:image/glassfish-4.1.1-{}".format(
			self.__BRANCH_NAME,
			image_type
		)
		
	def __image_name(self, image_type):
	
		return "miquelo/glassfish-4.1.1-{}:{}".format(
			image_type,
			self.__IMAGE_TAG
		)
		
	def __container_name(self, container_type, name):
	
		return "{}{}-{}".format(self.__base_name_str, container_type, name)
		
	def __prepare_public_key_file(self, container_name, user):

		path = os.path.expanduser("~/.caviar")
		if not os.path.exists(path):
			os.mkdir(path)
		path = os.path.join(path, "docker")
		if not os.path.exists(path):
			os.mkdir(path)
		path = os.path.join(path, "{}-{}.pem".format(container_name, user))
		if not os.path.exists(path):
			with open(path, "a"):
				pass
		return path
		
	def __container_id(self, image_type, container_name, binds):
		
		cont_list = self.__client.containers(all=True, filters={
			"name": container_name
		})
		if len(cont_list) > 0:
			cont = cont_list[0]
		else:
			cont = self.__client.create_container(
				image=self.__image_name(image_type),
				name=container_name,
				environment={
					# "DOCKER_CONTAINER_NAME": container_name
				},
				host_config=self.__client.create_host_config(
					binds=binds
				)
			)
		return cont["Id"]
		
	@property
	def server_node_dir(self):
	
		return caviar.provider.machinery.docker.server.NODE_DIR
		
	def server(self, name, authorized_key_paths=None):
	
		container_name = self.__container_name("server", name)
		appserver_public_key_path = self.__prepare_public_key_file(
			container_name,
			self.__APPSERVER_USER
		)
		
		all_authorized_key_paths = []
		all_authorized_key_paths.append(self.__mgmt_public_key_path)
		if authorized_key_paths is not None:
			all_authorized_key_paths.extend(authorized_key_paths)
			
		binds = {}
		binds.update({
			appserver_public_key_path: {
				"bind": "/usr/lib/glassfish4/.ssh/id_rsa.pub",
				"mode": "rw"
			}
		})
		binds.update({
			authorized_key_path: {
				"bind": "/usr/lib/glassfish4/.ssh/authorized_keys.dir" \
					"/authorized-key-{}.pem".format(i + 1),
				"mode": "ro"
			}
			for i, authorized_key_path
			in enumerate(all_authorized_key_paths)
		})
		return caviar.provider.machinery.docker.server.ServerMachine(
			self.__client,
			self.__container_id("server", container_name, binds),
			self.__APPSERVER_USER,
			appserver_public_key_path
		)

