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


class TestServerHelloEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_response = get(endpoint="/hello")

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
            "Hello, World!",
        )


class TestServerGoodbyeEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_response = get(endpoint="/goodbye")

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
            "Goodbye, World!",
        )


with GCM("Server") as server_tests:

    @GCM.add_setup("start server")
    def setUp():
        start_server()

    @GCM.add_teardown("stop server")
    def tearDown():
        stop_server()

    with GCM.add_group("/hello Endpoint"):

        @GCM.add_setup("making request to server")
        def setUp():
            GCM.server_response = get("/hello")

        with GCM.add_group("Response"):

            @GCM.add_test("is dict")
            def test(case):
                case.assertIsInstance(
                    case.server_response,
                    dict,
                )

            @GCM.add_test("keys")
            def test(case):
                case.assertEqual(
                    list(case.server_response.keys()),
                    [
                        "status",
                        "data",
                    ],
                )

            @GCM.add_test("status")
            def test(case):
                case.assertEqual(
                    case.server_response["status"],
                    "success",
                )

            @GCM.add_test("data")
            def test(case):
                case.assertEqual(
                    case.server_response["data"],
                    "Hello, World!",
                )

    with GCM.add_group("/goodbye Endpoint"):

        @GCM.add_setup("making request to server")
        def setUp():
            GCM.server_response = get("/goodbye")

        with GCM.add_group("Response"):

            @GCM.add_test("is dict")
            def test(case):
                case.assertIsInstance(
                    case.server_response,
                    dict,
                )

            @GCM.add_test("keys")
            def test(case):
                case.assertEqual(
                    list(case.server_response.keys()),
                    [
                        "status",
                        "data",
                    ],
                )

            @GCM.add_test("status")
            def test(case):
                case.assertEqual(
                    case.server_response["status"],
                    "success",
                )

            @GCM.add_test("data")
            def test(case):
                case.assertEqual(
                    case.server_response["data"],
                    "Goodbye, World!",
                )


server_tests.create_tests()
