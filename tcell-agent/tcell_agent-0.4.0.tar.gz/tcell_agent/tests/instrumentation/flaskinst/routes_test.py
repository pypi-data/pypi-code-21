import unittest

from functools import partial
from mock import Mock, patch

import tcell_agent
from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.flaskinst.routes import calculate_route_id, discover_route, get_methods
from tcell_agent.sanitize.sanitize_utils import USE_PYTHON_2_HASH

tcell_agent.instrumentation.flaskinst.routes.REPORT_ROUTE = True


def index():
    return "/"


class RoutesTest(unittest.TestCase):

    @classmethod
    def api(cls):
        return "/api"

    def upper_case_method_calculate_route_id_test(self):
        if USE_PYTHON_2_HASH:
            self.assertEqual("-8927252616038890182", calculate_route_id("GET", "/"))
        else:
            self.assertEqual("98246921", calculate_route_id("GET", "/"))

    def lower_case_method_calculate_route_id_test(self):
        if USE_PYTHON_2_HASH:
            self.assertEqual("-8927252616038890182", calculate_route_id("get", "/"))
        else:
            self.assertEqual("98246921", calculate_route_id("get", "/"))

    def methods_provided_get_methods_test(self):
        options = {"methods": ["GET", "POST"]}
        methods = get_methods(options, None)
        self.assertEqual(["GET", "POST"], methods)

    def view_func_methods_get_methods_test(self):
        options = {}
        view_func = Mock(methods=["PUT", "DELETE"])
        methods = get_methods(options, view_func)
        self.assertEqual(["PUT", "DELETE"], methods)

    def no_methods_get_methods_test(self):
        options = {}
        view_func = Mock(methods=None)
        methods = get_methods(options, view_func)
        self.assertEqual(["GET"], methods)

    def dynamic_discover_route_test(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_route", return_value=None) as patched_discover_route:
            discover_route("/", partial(index), options)

            patched_discover_route.assert_called_once_with(
                route_url="/",
                route_method="GET",
                route_target="tcell_agent.tests.instrumentation.flaskinst.routes_test.index",
                route_id=calculate_route_id("GET", "/"))

    def function_discover_route_test(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_route", return_value=None) as patched_discover_route:
            discover_route("/", index, options)

            patched_discover_route.assert_called_once_with(
                route_url="/",
                route_method="GET",
                route_target="tcell_agent.tests.instrumentation.flaskinst.routes_test.index",
                route_id=calculate_route_id("GET", "/"))

    def bound_method_discover_route_test(self):
        options = {"methods": ["GET"]}
        with patch.object(TCellAgent, "discover_route", return_value=None) as patched_discover_route:
            discover_route("/", RoutesTest.api, options)

            patched_discover_route.assert_called_once_with(
                route_url="/",
                route_method="GET",
                route_target="tcell_agent.tests.instrumentation.flaskinst.routes_test.api",
                route_id=calculate_route_id("GET", "/"))
