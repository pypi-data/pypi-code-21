from typing import List
from werkzeug.routing import Map, Rule


class Cove(object):
    def __init__(self):
        self.route_map = Map([])

    def reset(self):
        self.route_map = Map([])

    def route(self, path: str, methods: List[str] = None):
        """
        Adds a routing Rule to a Cove endpoint.

        See http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.Rule

        :param path: the relative path for the route e.g. '/hello'
        :param methods: allowed HTTP method names e.g. ['GET', 'POST']
        :return: the route decorator
        """

        def decorator(f):
            rule = Rule(path, endpoint=f, methods=methods)
            self.route_map.add(rule)
            return f

        return decorator


__all__ = (
    "Cove",
    "route",
)

_globalApp = Cove()

route = _globalApp.route
