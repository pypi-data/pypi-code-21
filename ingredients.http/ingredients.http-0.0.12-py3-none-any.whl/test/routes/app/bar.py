import cherrypy

from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from ingredients_http.router import Router
from ingredients_http.test.routes.app.validation_models.bar import RequestPostBar


class BarRouter(Router):
    def __init__(self):
        super().__init__(uri_base='bar')

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.model_in(cls=RequestPostBar)
    @cherrypy.tools.json_out()
    def post(self):
        return {}
