from contextional import GCM


def create_it(chain):

    desc = chain.pop()

    with GCM(desc) as it:

        if chain:

            GCM.includes(create_it(chain))

        else:

            @GCM.add_test("test description")
            def test(case):
                GCM.it

    return it




with GCM("A") as it:

    GCM.includes(create_it(["B", "C", "D"]))


it.create_tests()
