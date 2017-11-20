import requests
import json
import six

from tests.framework import (CapturedIOTestCase)
from globus_sdk.transfer.paging import PaginatedResource
from globus_sdk.transfer.response import IterableTransferResponse


class PagingSimulator(object):

    def __init__(self, n):
        self.n = n  # the number of simulated items

    def simulate_get(self, path, params=None,
                     headers=None, response_class=None, retry_401=True):
        """
        Simulates a paginated response from a Globus API get supporting limit,
        offset, and has next page
        """
        offset = params["offset"]
        limit = params["limit"]
        data = {}  # dict that will be treated as the json data of a response
        data["offset"] = offset
        data["limit"] = limit
        # fill data field
        data["DATA"] = []
        for i in range(offset, min(self.n, offset + limit)):
            data["DATA"].append({"value": i})
        # fill has_next_page field
        data["has_next_page"] = (offset + limit) < self.n

        # make the simulated response
        response = requests.Response()
        response._content = six.b(json.dumps(data))
        response.headers["Content-Type"] = "application/json"
        return IterableTransferResponse(response)


class PaginatedResourceTests(CapturedIOTestCase):

    def setUp(self):
        """
        Creates a PagingSimulator for testing PaginatedResources
        """
        super(PaginatedResourceTests, self).setUp()
        self.n = 25
        self.simulator = PagingSimulator(self.n)

    def test_data(self):
        """
        Gets data from PaginatedResource objects based on paging_simulator,
        confirms data is the expected range of numbers
        tests num_results < n, num_results > n, num_results = None,
        """
        # num_results < n
        less_results = self.n - 7
        pr_less = PaginatedResource(
            self.simulator.simulate_get, "path", {"params": {}},
            max_results_per_call=10, num_results=less_results)
        # confirm results
        for item, expected in zip(pr_less.data, range(less_results)):
            self.assertEqual(item["value"], expected)
        self.assertEqual(pr_less.num_results_fetched, less_results)

        # num_results > n
        more_results = self.n + 7
        pr_more = PaginatedResource(
            self.simulator.simulate_get, "path", {"params": {}},
            max_results_per_call=10, num_results=more_results)
        # confirm results
        for item, expected in zip(pr_more.data, range(self.n)):
            self.assertEqual(item["value"], expected)
        self.assertEqual(pr_more.num_results_fetched, self.n)

        # num_results = None (fetch all)
        pr_none = PaginatedResource(
            self.simulator.simulate_get, "path", {"params": {}},
            max_results_per_call=10, num_results=None)
        # confirm results
        for item, expected in zip(pr_none.data, range(self.n)):
            self.assertEqual(item["value"], expected)
        self.assertEqual(pr_none.num_results_fetched, self.n)

    def test_iterable_func(self):
        """
        Gets the generator from a PaginatedResource's iterable_func,
        sanity checks usage
        """
        pr = PaginatedResource(
            self.simulator.simulate_get, "path", {"params": {}},
            max_results_per_call=10, num_results=None)

        generator = pr.iterable_func()
        for i in range(self.n):
            self.assertEqual(six.next(generator)["value"], i)

        with self.assertRaises(StopIteration):
            six.next(generator)
