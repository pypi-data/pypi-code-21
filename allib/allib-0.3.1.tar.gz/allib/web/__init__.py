import importlib
import inspect
import json
import logging

import werkzeug.exceptions
import werkzeug.routing
import werkzeug.wrappers

from allib import di

# these imports are so that people can "import X from framework"
from werkzeug.wrappers import Response, Request #pylint: enable=ungrouped-imports

log = logging.getLogger(__name__)


def _lazy_import(string):
	try:
		return importlib.import_module(string)
	except ImportError:
		pass

	try:
		parts = string.split('.')
		mod_string = '.'.join(parts[:-1])
		mod = importlib.import_module(mod_string)
		attr_string = parts[-1]
		return getattr(mod, attr_string)
	except ImportError:
		raise ImportError('Could not import module %r or %r' % (string, mod_string))
	except AttributeError:
		raise ImportError('Module %r does not have an attribute %r' % (mod_string, attr_string))


class JsonResponse(werkzeug.wrappers.Response):
	def __init__(self, response, *args, **kwargs):
		kwargs.setdefault('mimetype', 'application/json')
		werkzeug.wrappers.Response.__init__(
			self, (json.dumps(response), '\n'), *args, **kwargs
		)


class Config(dict):
	pass


class Application:
	def __init__(self, name, debug=False, autoreload=None):
		self.name = name
		self.debug = debug
		self.autoreload = debug if autoreload is None else autoreload
		self.url_map = werkzeug.routing.Map()
		self.config = Config({'debug': self.debug})

		self.injector = di.Injector()
		self.injector.instances[Application] = self
		self.injector.instances[Config] = self.config

	def add_plugin(self, plugin):
		if isinstance(plugin, str):
			plugin = _lazy_import(plugin)
		if hasattr(plugin, '__plugin__'):
			if isinstance(plugin.__plugin__, str):
				plugin = getattr(plugin, plugin.__plugin__)
			else:
				plugin = plugin.__plugin__
		self.injector.register_plugin(plugin)

	def add_route(self, methods, path, view, **kwargs):
		if isinstance(methods, str):
			methods = (methods,)
		rule = werkzeug.routing.Rule(path, methods=methods, endpoint=view, **kwargs)
		self.url_map.add(rule)

	def add_routes(self, routes):
		for route in routes:
			self.add_route(methods=route[0], path=route[1], view=route[2])

	def add_route_set(self, path, route_set):
		if isinstance(route_set, str):
			route_set = _lazy_import(route_set)
		for route in route_set.get_routes(path):
			self.add_route(methods=route[0], path=route[1], view=route[2])

	def wsgi_app(self, environ, start_response):
		request = werkzeug.wrappers.Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def dispatch_request(self, request):
		try:
			endpoint, values = self.url_map.bind_to_environ(request.environ).match()
		except werkzeug.exceptions.HTTPException as exc:
			log.warning('HTTPException while URL matching %r', request, exc_info=True)
			return exc

		if isinstance(endpoint, str):
			endpoint = _lazy_import(endpoint)

		if inspect.isclass(endpoint):
			endpoint = self.injector.get(endpoint)

		try:
			response = endpoint(request, **values)
		except werkzeug.exceptions.BadRequestKeyError as exc:
			exc.description = "Missing data: %s" % ', '.join(
				repr(key) for key in exc.args
			)
			return exc
		except werkzeug.exceptions.HTTPException as exc:
			log.warning('HTTPException while calling view function', exc_info=True)
			return exc

		if isinstance(response, str):
			response = werkzeug.wrappers.Response(response)

		return response

	def run(self, host, port):
		from werkzeug.serving import run_simple
		run_simple(host, port, self.wsgi_app, self.debug, self.autoreload)

	def cli(self):
		import argparse
		parser = argparse.ArgumentParser()
		commands = parser.add_subparsers(dest='command')
		commands.required = True
		serve_parser = commands.add_parser('serve')
		serve_parser.add_argument('-b', '--bind', default='localhost')
		serve_parser.add_argument('-p', '--port', default='8000')
		args = parser.parse_args()
		if args.command == 'serve':
			self.run(args.bind, int(args.port))


class View:
	def __call__(self, request, **values):
		return self.render(request, **values)

	def render(self, request, **values):
		raise NotImplementedError('Views must implement render()')


class ViewSet:
	def __call__(self, request, **values):
		return getattr(self, request.method.lower())(request, **values)


class RestViewSet:
	methods = {
		'GET': ('list', 'show'),
		'POST': 'create',
		'PATCH': 'update',
		'PUT': 'update',
		'DELETE': 'delete',
	}

	def __call__(self, request, **values):
		if request.method == 'GET' or request.method == 'HEAD':
			method = self.methods['GET'][len(values)]
		else:
			method = self.methods[request.method]
		if not hasattr(self, method):
			msg = 'view set %r does not imlpement method %r for HTTP method %s' % (
					self, method, request.method)
			raise NotImplementedError(msg)
		return getattr(self, method)(request, **values)

	@classmethod
	def get_routes(cls, root_url, id_keyword='id'):
		return [
			(('HEAD', 'GET', 'POST'), root_url, cls),
			(('HEAD', 'GET', 'PATCH', 'PUT', 'DELETE'), '%s/<%s>' % (root_url, id_keyword), cls),
		]
