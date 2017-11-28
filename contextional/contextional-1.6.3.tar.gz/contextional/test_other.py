from contextional import GroupContextManager as GCM



with GCM("thing") as thing:
    @GCM.add_setup
    def setUp():
        pass


with GCM("other") as other:

    @GCM.add_test("stuff")
    def test(case):
        pass

    GCM.combine(
        thing,
    )


other.create_tests()
