import cherrypy

from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from ingredients_http.router import Router


class FooRouter(Router):
    def __init__(self):
        super().__init__(uri_base='foo')

    @Route()
    @cherrypy.tools.json_out()
    def get(self):
        return {}

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def post(self):
        data = cherrypy.request.json
        return data
