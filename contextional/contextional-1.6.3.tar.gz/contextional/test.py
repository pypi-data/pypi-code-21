from __future__ import print_function

import unittest

from contextional import GroupContextManager as GCM


class T(object):

    def assertThing(self, arg):
        assert arg == 4


GCM.utilize_asserts(T)



#
# with GCM("TEst") as t:
#
#     @t.add_test("stuff")
#     def test(case):
#         case.assertThing(4)
#
#     with t.add_group("other"):
#         @t.add_test("stuff")
#         def test(case):
#             case.assertThing(2)
#
#
# with GCM("Predefined Group") as PG:
#
#     @PG.add_test("value is 1")
#     def test(case):
#         case.assertEqual(
#             PG.value,
#             1,
#         )
#
#     with PG.add_group("Sub Group"):
#
#         @PG.add_test("value is still 1")
#         def test(case):
#             case.assertEqual(
#                 PG.value,
#                 1,
#             )

def multiplier(num_1, num_2):
    return num_1 * num_2


with GCM("value test") as vt:

    @vt.add_test("value")
    def test(case):
        case.assertEqual(
            vt.value,
            vt.expected_value,
        )

x = list("abcde")


with GCM("Main Group") as MG:

    @MG.add_test("sample")
    def test(case):
        # print(MG.defaultTestResult())
        pass

    @MG.add_teardown
    def tearDown():
        raise Exception()

    # @MG.add_test("is not foo")
    # def test(case):
    #     thing(case)
    #     pass

    with MG.add_group("Sub Group"):

        @MG.add_teardown
        def tearDown():
            # print(MG.defaultTestResult())
            raise Exception()


        # @MG.add_setup
        # def setUp(x=x):
        #     assert x

        with MG.add_group("Another Sub Group"):

            # @MG.add_teardown
            # def tearDown():
            #     raise Exception()

            @MG.add_test("is not foo")
            def test(case):
                thing(case)
                pass

            @MG.add_test("will not pass2")
            def test(case):
                case.fail()
                pass

            # with MG.add_group("Yet Another Sub Group"):
            #
            #     @MG.add_test("is not foo")
            #     def test(case):
            #         thing(case)
            #         pass

        with MG.add_group("Yet Another Sub Group"):

            @MG.add_test
            def test(case):
                thing(case)
                pass

        with MG.add_group("Yet Another, Different Sub Group"):

            @MG.add_setup
            def setUp():
                raise Exception()
                # pass

            with MG.add_group("With A Sub Group"):

                @MG.add_test("is not foo")
                def test(case):
                    pass


MG.create_tests(globals())


# Main Group
#   Sub Group
#     is not foo ... PASSED
#     will not pass ... FAILED


# class TestSomething(unittest.TestCase):
#
#     # @classmethod
#     # def setUpClass(self):
#     #     raise Exception()
#
#     def assertThing(self, arg):
#         assert arg == 4
#
#     # def setup_class(cls):
#     #     print("in setup_class")
#     #
#     # def setup_method(self, method):
#     #     print(method)
#     #     print ("\n%s:%s" % (type(self).__name__, method.__name__))
#
#     def teardown_method(self, method):
#         raise Exception()
#         pass
#
#     def tearDown(self):
#         raise Exception()
#         pass
#
#     def test_the_power(self):
#         thing(self)
#
#     def test_something_else(self):
#         assert hhh
#
#
# class TestAnotherSomething(unittest.TestCase):
#
#     def assertThing(self, arg):
#         assert arg == 4
#
#     # def setup_class(cls):
#     #     print("in setup_class")
#     #
#     # def setup_method(self, method):
#     #     print(method)
#     #     print ("\n%s:%s" % (type(self).__name__, method.__name__))
#
#     def teardown_method(self, method):
#         pass
#
#     def test_the_power(self):
#         thing(self)
#
#     def test_something_else(self):
#         assert hhh


def dec(func):
    func._nodeid = "hellothere"
    return func


def thing(case):
    case.assertNotEqual(
        "foo",
        "foo",
        msg="reasons!",
    )

# def thing2():
#     assert 2 == 3
#
# @dec
# def test_things():
#     pass


# class TestIt(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         for thing in dir(cls):
#             print(thing)
#         raise Exception()
#
#     def setUp(self):
#         pass
#
#     def test_it_1(self):
#         pass
#
#     def test_it_2(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#     @classmethod
#     def tearDownClass(cls):
#         raise Exception()
#
#
# def suite():
#
#     suite = unittest.TestSuite()
#     suite.addTest (TestIt("test_it_1"))
#     suite.addTest (TestIt("test_it_2"))
#     return suite
#
# if __name__ == "__main__":
#
#     runner = unittest.TextTestRunner()
#
#     test_suite = suite()
#
#     runner.run (test_suite)

# def test():
#     pass


class FakeStream(object):

    def __init__(self):
        self.f = ""

    def write(self, text):
        self.f += text

    def flush(self):
        pass


fs = FakeStream()


class SilentTestRunner(unittest.TextTestRunner):

    def __init__(self, *args, **kwargs):
        global fs
        kwargs["stream"] = fs
        super(SilentTestRunner, self).__init__(*args, **kwargs)


class TestIt(unittest.TestCase):

    def test_things(self):
        pass


if __name__ == '__main__':
#     # x = unittest.main(testRunner=SilentTestRunner, exit=False)
    x = unittest.main()
#     # print(fs.f)
