import inspect
import logging
from abc import ABCMeta
from typing import List, Callable

import cherrypy
from sqlalchemy.orm import Query

from ingredients_http.request_methods import RequestMethods


class Router(object):
    __metaclass__ = ABCMeta

    def __init__(self, uri_base=None):
        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))

        self.uri_base = uri_base
        self.mount = None

    def __register_route(self, dispatcher: cherrypy.dispatch.RoutesDispatcher, uri_prefix: str, route: str,
                         action: Callable,
                         methods: List[RequestMethods] = None):
        if methods is None:
            methods = [RequestMethods.GET]

        method_names = [rm.value for rm in methods]
        if uri_prefix == '/':
            complete_uri = uri_prefix + (self.uri_base if self.uri_base is not None else '')
        else:
            complete_uri = uri_prefix + ("/" + self.uri_base if self.uri_base is not None else '')

        complete_uri = complete_uri + ("/" + route if route else '')

        self.logger.debug(
            "Registering route " + complete_uri + " with action " + action.__name__ + " and allowed methods " + str(
                method_names))

        dispatcher.connect(self.__module__ + "." + self.__class__.__name__ + "." + action.__name__,
                           complete_uri, controller=self, action=action.__name__, conditions=dict(method=method_names))

    def setup_routes(self, dispatcher: cherrypy.dispatch.RoutesDispatcher, uri_prefix: str):

        for member in [getattr(self, attr) for attr in dir(self)]:
            if inspect.ismethod(member) and hasattr(member, '_route'):
                self.__register_route(dispatcher, uri_prefix, member._route, member, member._methods)

    def paginate(self, db_cls, response_cls, limit, marker, starting_query=None):
        if starting_query is None:
            starting_query = Query(db_cls)
        resp_objects = []
        with cherrypy.request.db_session() as session:
            starting_query.session = session
            db_objects = starting_query.order_by(db_cls.created_at.desc())

            if marker is not None:
                marker = session.query(db_cls).filter(db_cls.id == marker).first()
                if marker is None:
                    raise cherrypy.HTTPError(status=400, message="Unknown marker ID")
                db_objects = db_objects.filter(db_cls.created_at < marker.created_at)

            db_objects = db_objects.limit(limit + 1)

            for db_object in db_objects:
                resp_objects.append(response_cls.from_database(db_object))

        more_pages = False
        if len(resp_objects) > limit:
            more_pages = True
            del resp_objects[-1]  # Remove the last item to reset back to original limit

        return resp_objects, more_pages
