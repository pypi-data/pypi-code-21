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
Management module.
"""

# Using REST Interfaces to Administer GlassFish Server
# https://docs.oracle.com/cd/E18930_01/html/821-2416/gjipx.html#scrolltoc

import io

import caviar
import caviar.network

# TODO Test coverage
class ManagementError(BaseException):

	def __init__(self, exit_code, message):
	
		super().__init__(exit_code, message)
		self.__exit_code = exit_code
		self.__message = message
		
	# TODO Test coverage
	@property
	def exit_code(self):
	
		return self.__exit_code
		
	# TODO Test coverage
	@property
	def message(self):
	
		return self.__message
		
class Management:

	"""
	Management client.
	"""

	def __init__(self, das_machine, port, http_auth,
			network_module=caviar.network):
	
		http_resource = network_module.http_resource(
			protocol="https",
			host=das_machine.host,
			port=port,
			auth=http_auth,
			headers={
				"X-Requested-By": [ "GlassFish REST HTML interface" ]
			}
		)
		self.__domain_get = ManagementRequest(
			http_resource.push("management").push("domain"),
			"GET"
		)
		self.__domain = None
		
	# TODO Test coverage
	def domain(self):
	
		"""
		Retrieve domain root resource.
		
		:rtype:
		   ManagementResource
		:return:
		   The domain root resource.
		"""
		
		if self.__domain is None:
			self.__domain = self.__domain_get()
			self.__domain.raise_not_success()
		return self.__domain
		
# TODO Test coverage
class ManagementResource:

	def __init__(self, http_resource, data):
	
		self.__command = data["command"]
		self.__exit_code = data["exit_code"]
		self.__message = data.get("message")
		self.__extra_properties = ManagementExtraProperties(
			http_resource,
			data.get("extraProperties", {})
		)
		
	# TODO Test coverage
	@property
	def command(self):
	
		return self.__command
		
	# TODO Test coverage
	@property
	def exit_code_success(self):
	
		return self.__exit_code == "SUCCESS"
		
	# TODO Test coverage
	@property
	def exit_code_failure(self):
	
		return self.__exit_code == "FAILURE"
		
	# TODO Test coverage
	@property
	def message(self):
	
		return self.__message
		
	# TODO Test coverage
	@property
	def extra_properties(self):
	
		return self.__extra_properties
		
	# TODO Test coverage
	def raise_not_success(self):
	
		if not self.exit_code_success:
			raise ManagementError(self.__exit_code, self.__message)
		return self
		
# TODO Test coverage
class ManagementExtraProperties:

	def __init__(self, http_resource, data):
	
		self.__commands = ManagementCommands(
			http_resource,
			data.get("commands", [])
		)
		self.__methods = ManagementMethods(
			http_resource,
			data.get("methods", [])
		)
		self.__entity = ManagementEntity(
			data.get("entity", {})
		)
		self.__child_resources = ManagementChildResources(
			http_resource,
			data.get("childResources", {})
		)
		
	# TODO Test coverage
	@property
	def commands(self):
	
		return self.__commands
		
	# TODO Test coverage
	@property
	def methods(self):
	
		return self.__methods
		
	# TODO Test coverage
	@property
	def entity(self):
	
		return self.__entity
		
	# TODO Test coverage
	@property
	def child_resources(self):
	
		return self.__child_resources
		
# TODO Test coverage
class ManagementCommands:

	def __init__(self, http_resource, data):
	
		for command_data in data:
			setattr(
				self,
				command_data["command"].replace("-", "_"),
				ManagementCommand(
					http_resource.push(command_data["path"]),
					command_data["method"]
				)
			)
			
# TODO Test coverage
class ManagementCommand:

	def __init__(self, http_resource, method_name):
	
		self.__resource_get = ManagementRequest(http_resource, "GET")
		self.__method_name = method_name
		self.__request = None
		
	# TODO Test coverage
	def __call__(self, **kvargs):
	
		if self.__request is None:
			res = self.__resource_get()
			res.raise_not_success()
			self.__request = res.extra_properties.methods[self.__method_name]
		return self.__request(**kvargs)
		
# TODO Test coverage
class ManagementMethods:

	def __init__(self, http_resource, data):
	
		self.__requests = {}
		for method_data in data:
			if "name" in method_data:
				method_name = method_data["name"]
				request = ManagementRequest(
					http_resource,
					method_name,
					ManagementParameters(
						self.__parameters(
							ManagementQueryParameter,
							method_data.get("queryParameters", {})
						),
						self.__parameters(
							ManagementMessageParameter,
							method_data.get("messageParameters", {})
						)
					)
				)
				self.__requests[method_name] = request
				setattr(
					self,
					method_name.lower(),
					request
				)
				
	# TODO Test coverage
	def __getitem__(self, key):
	
		return self.__requests[key]
		
	def __parameters(self, param_class, params_data):
	
		return {
			param_name.replace("-", "_"): param_class(
				param_name,
				param_data.get("defaultValue"),
				param_data.get("acceptableValues"),
				param_data["type"],
				param_data.get("optional", False),
				param_data.get("key", False)
			)
			for param_name, param_data in params_data.items()
		}
		
# TODO Test coverage
class ManagementEntity:

	def __init__(self, data):
	
		for name, value in data.items():
			setattr(self, name, value)
			
# TODO Test coverage
class ManagementChildResources:

	def __init__(self, http_resource, data):
	
		self.__children = {
			name: ManagementChildResource(http_resource.ref(url))
			for name, url
			in data.items()
		}
		
	# TODO Test coverage
	def __iter__(self):
	
		return self.__children.__iter__()
		
	# TODO Test coverage
	def __getitem__(self, key):
	
		return self.__children[key].get()
		
	# TODO Test coverage
	def items(self):
	
		for name, child in self.__children.items():
			yield ( name, child.get() )
			
	# TODO Test coverage
	def cache_evict(self):
	
		for _, child in self.__children.items():
			child.cache_evict()
			
# TODO Test coverage
class ManagementChildResource:

	def __init__(self, http_resource):
	
		self.__resource = None
		self.__resource_get = ManagementRequest(http_resource, "GET")
		
	# TODO Test coverage
	def get(self):
	
		if self.__resource is None:
			self.__resource = self.__resource_get()
		return self.__resource
		
	# TODO Test coverage
	def cache_evict(self):
	
		self.__resource = None
		
# TODO Test coverage
class ManagementRequest:

	def __init__(self, http_resource, method_name, params=None):
	
		self.__http_resource = http_resource
		self.__method_name = method_name
		self.__params = params or ManagementParameters({}, {})
		
	# TODO Test coverage
	def __call__(self, **kvargs):
	
		req = self.__http_resource.request(self.__method_name)
		
		remaining_required_param_names = [
			param_name
			for param_name, param in self.__params.items()
			if param.is_required()
		]
		for param_name, param_value in kvargs.items():
			if param_name in remaining_required_param_names:
				remaining_required_param_names.remove(param_name)
			try:
				self.__params[param_name].apply(req, param_value)
			except KeyError:
				raise AttributeError("Unknown parameter: {}".format(
					param_name
				))
		if len(remaining_required_param_names) > 0:
			raise AttributeError("Missing required parameters: {}".format(
				remaining_required_param_names
			))
			
		resp = req.perform()
		if resp.status_code != 200:
			raise BaseException(
				"Bad HTTP response status {} for request {} {}\n{}".format(
					resp.status_code,
					req.method,
					req.path,
					resp.content
				)
			)
		return ManagementResource(self.__http_resource, resp.content)
		
# TODO Test coverage
class ManagementParameters:

	def __init__(self, query_params, msg_params):
	
		self.__params = {}
		self.__params.update(query_params)
		self.__params.update(msg_params)
		
	# TODO Test coverage
	def __iter__(self):
	
		return self.__params.__iter__()
		
	# TODO Test coverage
	def __getitem__(self, key):
	
		return self.__params[key]
		
	# TODO Test coverage
	def items(self):
	
		for name, value in self.__params.items():
			yield ( name, value )
			
# TODO Test coverage
class ManagementParameter:

	def __init__(self, name, default_value, acceptable_values, param_type,
			optional, key):
	
		self.__name = name
		self.__default_value = default_value
		self.__param_type = param_type
		self.__optional = optional
		self.__key = key
		
		self.__inferred_acceptable_values = [
			self.__infer(acceptable_value)
			for acceptable_value in acceptable_values
		] if acceptable_values is not None else None
		
	def __infer(self, value):
	
		if self.is_boolean():
			return bool(value)
		if self.is_int():
			return int(value)
		if self.is_file():
			return value
		return str(value)
		
	# TODO Test coverage
	@property
	def name(self):
	
		return not self.__name
		
	# TODO Test coverage
	@property
	def default_value(self):
	
		return not self.__default_value
		
	# TODO Test coverage
	def is_required(self):
	
		return not self.__optional and self.__default_value is None
		
	# TODO Test coverage
	def is_boolean(self):
	
		return self.__param_type == "boolean"
		
	# TODO Test coverage
	def is_int(self):
	
		return self.__param_type == "int"
		
	# TODO Test coverage
	def is_string(self):
	
		return self.__param_type == "string"
		
	# TODO Test coverage
	def is_file(self):
	
		return self.__param_type == "java.io.File"
		
	# TODO Test coverage
	def is_key(self):
	
		return not self.__key
		
	# TODO Test coverage
	def apply(self, req, value):
	
		inferred_value = self.__infer(value)
		if self.__inferred_acceptable_values is not None \
				and inferred_value in self.__inferred_acceptable_values:
			raise AttributeError(
				"Unacceptable value for parameter '{}': {}".format(
					self.__name,
					inferred_value
				)
			)
		self.apply_impl(req, self.__name, inferred_value)
		
# TODO Test coverage
class ManagementQueryParameter(ManagementParameter):

	def __init__(self, name, default_value, acceptable_values, param_type,
			optional, key):
			
		super().__init__(
			name,
			default_value,
			acceptable_values,
			param_type,
			optional,
			key
		)
		
	# TODO Test coverage
	def apply_impl(self, req, name, value):
	
		req.query_param(name, value)
		
# TODO Test coverage
class ManagementMessageParameter(ManagementParameter):

	def __init__(self, name, default_value, acceptable_values, param_type,
			optional, key):
			
		super().__init__(
			name,
			default_value,
			acceptable_values,
			param_type,
			optional,
			key
		)
		
	# TODO Test coverage
	def apply_impl(self, req, name, value):
	
		if self.is_file():
			req.file_param(name, value)
		else:
			req.data_param(name, value)

