from contextional import GCM
import unittest


def start_server():
    # pretend like this does something
    pass


def stop_server():
    # pretend like this does something
    pass


RESPONSES = {
    "/hello": {
        "status": "success",
        "data": "Hello, World!",
    },
    "/goodbye": {
        "status": "success",
        "data": "Goodbye, World!",
    },
}


def get(endpoint):
    # pretend like this does something
    return RESPONSES.get(endpoint, {"status": "404"})


def setUpModule():
    start_server()


def tearDownModule():
    stop_server()


class ServerEndpointContext(object):

    @classmethod
    def setUpClass(cls):
        cls.server_response = get(endpoint=cls.endpoint)

    def test_response_is_dict(self):
        self.assertIsInstance(
            self.server_response,
            dict,
        )

    def test_response_keys(self):
        self.assertEqual(
            list(self.server_response.keys()),
            [
                "status",
                "data",
            ],
        )

    def test_response_status(self):
        self.assertEqual(
            self.server_response["status"],
            "success",
        )

    def test_response_data(self):
        self.assertEqual(
            self.server_response["data"],
            self.expected_data,
        )


class TestServerHelloEndpoint(ServerEndpointContext, unittest.TestCase):

    endpoint = "/hello"
    expected_data = "Hello, World!"


class TestServerGoodbyeEndpoint(ServerEndpointContext, unittest.TestCase):

    endpoint = "/goodbye"
    expected_data = "Goodbye, World!"


endpoint_details = [
    ("/hello", "Hello, World!"),
    ("/goodbye", "Goodbye, World!"),
]


with GCM("Server") as server_tests:

    @GCM.add_setup("start server")
    def setUp():
        start_server()

    @GCM.add_teardown("stop server")
    def tearDown():
        stop_server()

    for endpoint, data in endpoint_details:

        with GCM.add_group(f"{endpoint} Endpoint"):

            @GCM.add_setup("making request to server")
            def setUp(endpoint=endpoint, data=data):
                GCM.server_response = get(endpoint)
                GCM.expected_data = data

            with GCM.add_group("Response"):

                @GCM.add_test("is dict")
                def test(case):
                    case.assertIsInstance(
                        GCM.server_response,
                        dict,
                    )

                @GCM.add_test("keys")
                def test(case):
                    case.assertEqual(
                        list(GCM.server_response.keys()),
                        [
                            "status",
                            "data",
                        ],
                    )

                @GCM.add_test("status")
                def test(case):
                    case.assertEqual(
                        GCM.server_response["status"],
                        "success",
                    )

                @GCM.add_test("data")
                def test(case):
                    case.assertEqual(
                        GCM.server_response["data"],
                        GCM.expected_data,
                    )


server_tests.create_tests()
