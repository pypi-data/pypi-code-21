from io import BytesIO
from unittest import TestCase
from dataclay.core.management.classmgr import MetaClass, Property, Type, Operation

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

# FIXME: Correct this tests


class ContainerGeneric(TestCase):
    params = []
    mutable_params = []
    nullable_fields = []
    class_under_test = None

    def test_args(self):
        t = self.class_under_test(**dict(self.params))

        for key, val in self.params:
            self.assertEqual(getattr(t, key), val)

    def test_serialization(self):
        t = self.class_under_test(**dict(self.params))
        s = BytesIO()

        t.serialize(s)
        serialization_size = s.tell()
        s.write('EOF')  # sentinel that should not be read by deserialization
        s.seek(0)
        t_bis = t.deserialize(s)
        self.assertEqual(serialization_size, s.tell(),
                         "Deserialization has consumed {} bytes instead of {}".format(
                             s.tell(), serialization_size))

        for field, value in self.params:
            # Serialized assertion
            self.assertEqual(getattr(t, field), value)

            # ToDo: Change field=="parameters"

            if field == "parameters":
                for v in getattr(t_bis, field):
                    # print '\ncheck types inside parameters of ImplStubInfo'
                    c_bool, st_list = t_bis.type_equal(getattr(t_bis, field)[v], value[v])
                    self.assertTrue(c_bool)
                    # print '\ntype fields not set:'
                    # for st in st_list:
                    #     print st

            if not (type(getattr(t_bis, field)) is list
                    or (type(getattr(t_bis, field))) is set
                    or isinstance(getattr(t_bis, field), Type)
                    or (type(getattr(t_bis, field)) is dict)):
                # Deserialized assertion for not nested params
                self.assertEqual(getattr(t_bis, field), value)

            if isinstance(getattr(t_bis, field), Type):
                # Deserialized assertion for Type params
                # print '\ncheck', field
                c_bool, st_list = t_bis.type_equal(getattr(t_bis, field), value)
                self.assertTrue(c_bool)
                # print '\n', field, 'fields not set:'
                # for st in st_list:
                #     print st

            if not isinstance(getattr(t_bis, field), Type) \
                    and type(getattr(t_bis, field)) is list \
                    and len(getattr(t_bis, field)) > 0\
                    and isinstance(getattr(t_bis, field)[0], Property):
                # ToDo: Change the way to do it without l
                # Deserialized assertions for Property params
                l = 0
                for x in getattr(t_bis, field):
                    # print '\ncheck', field
                    c_bool, st_list = t_bis.prop_equal(x, value, l)

                    # print '\ncheck type inside', field
                    ct_bool, stt_list = t_bis.type_equal(x.type, value[l].type)
                    self.assertTrue(ct_bool)
                    # print "\ntype fields not set:"
                    # for stt in stt_list:
                    #     print stt

                    l += 1

                    self.assertTrue(c_bool)
                    # print "\n", field, "fields not set:"
                    # for st in st_list:
                    #     print st

            if type(getattr(t_bis, field)) is set and getattr(t_bis, field) is not None:
                # Deserialized assertion for Operation params
                # ToDo: Change the way to do it without z and h
                z = 0
                for x in getattr(t, field):
                    # print '\ncheck', field
                    h = 0
                    for y in value:
                        # ToDo: Change field != contracts
                            if z == h and field != "contracts":
                                # print '\ncheck types inside operations'
                                ct_bool, stt_list = t_bis.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                # print "\ntype fields not set:"
                                # for stt in stt_list:
                                #     print stt

                                op_bool, st_op = t_bis.op_equal(x, y, True)
                                self.assertTrue(op_bool)
                                # print "\n", field, "fields not set:"
                                # for st in st_op:
                                #     print st

                            h += 1
                    z += 1

    def test_serialization_chain(self):
        t = self.class_under_test(**dict(self.params))
        s = BytesIO()

        t.serialize(s)
        t.serialize(s)
        serialization_size = s.tell()
        s.write('EOF')  # sentinel that should not be read by deserialization
        s.seek(0)
        t_bis1 = t.deserialize(s)
        t_bis2 = t.deserialize(s)
        self.assertEqual(serialization_size, s.tell(),
                         "Deserialization has consumed {} bytes instead of {}".format(
                             s.tell(), serialization_size))

        for field, value in self.params:
            # Serialized assertion
            self.assertEqual(getattr(t, field), value)

            if field == "parameters":
                for v in getattr(t_bis1, field):
                    # print '\ncheck types inside parameters of ImplStubInfo'
                    c_bool, st_list = t_bis1.type_equal(getattr(t_bis1, field)[v], value[v])
                    self.assertTrue(c_bool)
                    """print '\ntype fields not set:'
                    for st in st_list:
                        print st
                    """

            if not (type(getattr(t_bis1, field)) is list
                    or (type(getattr(t_bis1, field))) is set
                    or isinstance(getattr(t_bis1, field), Type)
                    or (type(getattr(t_bis1, field)) is dict)):
                # Deserialized assertion for not nested params 1
                self.assertEqual(getattr(t_bis1, field), value)

            if isinstance(getattr(t_bis1, field), Type):
                # Deserialized assertion for Type params 1
                # print '\ncheck types'
                c_bool, st_list = t_bis1.type_equal(getattr(t_bis1, field), value)
                self.assertTrue(c_bool)
                """print '\ntype fields not set:'
                for st in st_list:
                    print st
                """

            if not isinstance(getattr(t_bis1, field), Type) \
                    and type(getattr(t_bis1, field)) is list \
                    and len(getattr(t_bis1, field)) > 0\
                    and isinstance(getattr(t_bis1, field)[0], Property):
                # Deserialized assertions for Property params 1
                l = 0
                for x in getattr(t_bis1, field):
                    # print '\ncheck properties'
                    c_bool, st_list = t_bis1.prop_equal(x, value, l)

                    # print '\ncheck types inside properties'
                    ct_bool, stt_list = t_bis1.type_equal(x.type, value[l].type)
                    self.assertTrue(ct_bool)
                    """print "\ntype fields not set:"
                    for stt in stt_list:
                        print stt
                    """

                    l += 1

                    self.assertTrue(c_bool)
                    """print "\nproperty fields not set:"
                    for st in st_list:
                        print st
                    """

            if type(getattr(t_bis1, field)) is set and getattr(t_bis1, field) is not None:
                # Deserialized assertion for Operation params 1
                z = 0
                for x in getattr(t, field):
                    # print '\ncheck operations'
                    h = 0
                    for y in value:
                            if z == h and field != "contracts":
                                # print '\ncheck types inside operations'
                                ct_bool, stt_list = t_bis1.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                """print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt
                                """

                                op_bool, st_op = t_bis1.op_equal(x, y, True)
                                self.assertTrue(op_bool)
                                """print "\noperation fields not set:"
                                for st in st_op:
                                    print st
                                """
                            h += 1
                    z += 1

            if field == "parameters":
                for v in getattr(t_bis2, field):
                    # print '\ncheck types inside parameters of ImplStubInfo'
                    c_bool, st_list = t_bis2.type_equal(getattr(t_bis2, field)[v], value[v])
                    self.assertTrue(c_bool)
                    """print '\ntype fields not set:'
                    for st in st_list:
                        print st
                    """

            if not (type(getattr(t_bis2, field)) is list
                    or (type(getattr(t_bis2, field))) is set
                    or isinstance(getattr(t_bis2, field), Type)
                    or (type(getattr(t_bis2, field)) is dict)):
                # Deserialized assertion for not nested params 2
                self.assertEqual(getattr(t_bis2, field), value)

            if isinstance(getattr(t_bis2, field), Type):
                # Deserialized assertion for Type params 2
                # print '\ncheck types'
                c_bool, st_list = t_bis2.type_equal(getattr(t_bis2, field), value)
                self.assertTrue(c_bool)
                """print '\ntype fields not set:'
                for st in st_list:
                    print st
                """

            if not isinstance(getattr(t_bis2, field), Type) \
                    and type(getattr(t_bis2, field)) is list \
                    and len(getattr(t_bis2, field)) > 0\
                    and isinstance(getattr(t_bis2, field)[0], Property):
                # Deserialized assertions for Property params 2
                l = 0
                for x in getattr(t_bis2, field):
                    # print '\ncheck properties'
                    c_bool, st_list = t_bis2.prop_equal(x, value, l)

                    # print '\ncheck types inside properties'
                    ct_bool, stt_list = t_bis2.type_equal(x.type, value[l].type)
                    self.assertTrue(ct_bool)
                    """print "\ntype fields not set:"
                    for stt in stt_list:
                        print stt
                    """

                    l += 1

                    self.assertTrue(c_bool)
                    """print "\nproperty fields not set:"
                    for st in st_list:
                        print st
                    """

            if type(getattr(t_bis2, field)) is set and getattr(t_bis2, field) is not None:
                # Deserialized assertion for Operation params 2
                z = 0
                for x in getattr(t, field):
                    # print '\ncheck operations'
                    h = 0
                    for y in value:
                            if z == h and field != "contracts":
                                # print '\ncheck types inside operations'
                                ct_bool, stt_list = t_bis2.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                """print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt
                                """

                                op_bool, st_op = t_bis2.op_equal(x, y, True)
                                self.assertTrue(op_bool)
                                """print "\noperation fields not set:"
                                for st in st_op:
                                    print st
                                """
                            h += 1
                    z += 1

    def test_serialization_with_nulls(self):
        for n in self.nullable_fields:
            params = dict(self.params)
            del params[n]
            t = self.class_under_test(**params)
            self.assertIsNone(getattr(t, n, None))
            s = BytesIO()

            t.serialize(s)
            serialization_size = s.tell()
            s.write('EOF')  # sentinel that should not be read by deserialization
            s.seek(0)
            t_bis = t.deserialize(s)
            self.assertEqual(serialization_size, s.tell(),
                             "Deserialization has consumed less bytes than serialization")

            for field, value in params.iteritems():
                # Serialized assertion
                self.assertEqual(getattr(t,field), value)

                if field == "parameters":
                    for v in getattr(t_bis, field):
                        # print '\ncheck types inside parameters of ImplStubInfo'
                        c_bool, st_list = t_bis.type_equal(getattr(t_bis, field)[v], value[v])
                        self.assertTrue(c_bool)
                        """print '\ntype fields not set:'
                        for st in st_list:
                            print st
                        """

                if not (type(getattr(t_bis, field)) is list
                        or type(getattr(t_bis, field)) is set
                        or isinstance(getattr(t_bis, field), Type)
                        or type(getattr(t_bis, field)) is dict):
                    # Deserialized assertion for not nested params
                    self.assertEqual(getattr(t_bis, field), value)

                if isinstance(getattr(t_bis, field), Type):
                    # Deserialized assertion for Type params
                    # print '\ncheck types'
                    c_bool, st_list = t_bis.type_equal(getattr(t_bis, field), value)
                    self.assertTrue(c_bool)
                    """print '\ntype fields not set:'
                    for st in st_list:
                        print st
                    """

                if not isinstance(getattr(t_bis, field), Type) \
                        and type(getattr(t_bis, field)) is list \
                        and len(getattr(t_bis, field)) > 0 \
                        and isinstance(getattr(t_bis, field)[0], Property):
                    # Deserialized assertions for Property params
                    l = 0
                    for x in getattr(t_bis, field):
                        # print '\ncheck properties'
                        c_bool, st_list = t_bis.prop_equal(x, value, l)

                        # print '\ncheck types inside properties'
                        ct_bool, stt_list = t_bis.type_equal(x.type, value[l].type)
                        self.assertTrue(ct_bool)
                        """print "\ntype fields not set:"
                        for stt in stt_list:
                            print stt
                        """

                        l += 1

                        self.assertTrue(c_bool)
                        """print "\nproperty fields not set:"
                        for st in st_list:
                            print st
                        """

                if type(getattr(t_bis, field)) is set and getattr(t_bis, field) is not None:
                    # Deserialized assertion for Operation params
                    z = 0
                    for x in getattr(t, field):
                        # print '\ncheck operations'
                        h = 0
                        for y in value:
                            if z == h and field != "contracts":
                                # print '\ncheck types inside operations'
                                ct_bool, stt_list = t_bis.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                """print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt
                                """

                                op_bool, st_op = t_bis.op_equal(x, y, True)
                                self.assertTrue(op_bool)
                                """print "\noperation fields not set:"
                                for st in st_op:
                                    print st
                                """
                            h += 1
                        z += 1
