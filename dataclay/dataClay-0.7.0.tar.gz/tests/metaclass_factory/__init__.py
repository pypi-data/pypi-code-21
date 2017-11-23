from dataclay.managers.classes.factory import MetaClassFactory
from test_classes import TestClass
import unittest
from io import BytesIO
from dataclay.core.management import baseclass
from dataclay.core.management.classmgr import MetaClass, Property, Type, Operation

"""UnitTests for the MetaClass Factory - dataclay/managers/classes/factory.py"""
__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'


class MetaClassFactoryContainer(unittest.TestCase):
    params = ["namespace",
              "name",
              "parentType",
              "properties",
              "operations",
              "isAbstract",
              "languageDepInfos",
              ]

    nullable_fields = ["parentType"]

    def test_serialization(self):
        mfc = MetaClassFactory(namespace="classTest", responsible_account="registrator")

        mfc.add_class(TestClass)

        for t in mfc.classes:
            s = BytesIO()
            t.serialize(s)

            serialization_size = s.tell()
            s.write('EOF')  # sentinel that should not be read by deserialization
            s.seek(0)
            t_bis = t.deserialize(s)
            self.assertEqual(serialization_size, s.tell(),
                             "Deserialization has consumed {} bytes instead of {}".format(
                                 s.tell(), serialization_size))

            for field in self.params:
                # Deserialized assertion
                if not (type(getattr(t_bis, field)) is list
                        or (type(getattr(t_bis, field))) is set
                        or isinstance(getattr(t_bis, field), Type)
                        or field == "languageDepInfos"):
                    print "F", field, "1"
                    self.assertEqual(getattr(t, field), getattr(t_bis, field))

                if not isinstance(getattr(t_bis, field), Type) \
                        and type(getattr(t_bis, field)) is list \
                        and len(getattr(t_bis, field)) > 0 \
                        and isinstance(getattr(t_bis, field)[0], Property):
                    # ToDo: Change the way to do it without l
                    # Deserialized assertions for Property params
                    print "F", field, "2"
                    z = 0
                    for x in getattr(t_bis, field):
                        print '\ncheck properties'
                        h = 0
                        for y in getattr(t, field):
                            if z == h:

                                prop_bool, st_prop = baseclass.ManagementObject.prop_equal(x, y)
                                self.assertTrue(prop_bool)
                                print "\nproperties fields not set:"
                                for st in st_prop:
                                    print st, "\n"
                            h += 1
                        z += 1

                if field == "operations" and getattr(t_bis, field) is not None:
                    # Deserialized assertion for Operation params
                    print "F", field, "3"
                    # ToDo: Change the way to do it without z and h
                    z = 0
                    for x in getattr(t, field):
                        print '\ncheck operations'
                        h = 0
                        for y in getattr(t_bis, field):
                            if z == h:

                                print '\ncheck types inside operations'
                                ct_bool, stt_list = baseclass.ManagementObject.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt, "\n"

                                op_bool, st_op = baseclass.ManagementObject.op_equal(x, y)

                                self.assertTrue(op_bool)
                                print "\noperation fields not set:"
                                for st in st_op:
                                    print st, "\n"
                            h += 1
                        z += 1

    def test_serialization_chain(self):
        mfc = MetaClassFactory(namespace="classTest", responsible_account="registrator")

        mfc.add_class(TestClass)

        for t in mfc.classes:

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

            for field in self.params:
                # Deserialized assertion for t_bis1
                if not (type(getattr(t_bis1, field)) is list
                        or (type(getattr(t_bis1, field))) is set
                        or isinstance(getattr(t_bis1, field), Type)
                        or field == "languageDepInfos"):
                    print "F", field, "1"
                    self.assertEqual(getattr(t, field), getattr(t_bis1, field))

                if not isinstance(getattr(t_bis1, field), Type) \
                        and type(getattr(t_bis1, field)) is list \
                        and len(getattr(t_bis1, field)) > 0 \
                        and isinstance(getattr(t_bis1, field)[0], Property):
                    # ToDo: Change the way to do it without z and h
                    # Deserialized assertions for Property params for t_bis1
                    print "F", field, "2"
                    z = 0
                    for x in getattr(t_bis1, field):
                        print '\ncheck properties'
                        h = 0
                        for y in getattr(t, field):
                            if z == h:

                                prop_bool, st_prop = baseclass.ManagementObject.prop_equal(x, y)
                                self.assertTrue(prop_bool)
                                print "\nproperties fields not set:"
                                for st in st_prop:
                                    print st, "\n"
                            h += 1
                        z += 1

                if field == "operations" and getattr(t_bis1, field) is not None:
                    # Deserialized assertion for Operation params for t_bis1
                    print "F", field, "3"
                    # ToDo: Change the way to do it without z and h
                    z = 0
                    for x in getattr(t, field):
                        print '\ncheck operations'
                        h = 0
                        for y in getattr(t_bis1, field):
                            if z == h:

                                print '\ncheck types inside operations'
                                ct_bool, stt_list = baseclass.ManagementObject.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt, "\n"

                                op_bool, st_op = baseclass.ManagementObject.op_equal(x, y)

                                self.assertTrue(op_bool)
                                print "\noperation fields not set:"
                                for st in st_op:
                                    print st, "\n"
                            h += 1
                        z += 1

                # Deserialized assertion for t_bis2
                if not (type(getattr(t_bis2, field)) is list
                        or (type(getattr(t_bis2, field))) is set
                        or isinstance(getattr(t_bis2, field), Type)
                        or field == "languageDepInfos"):
                    print "F", field, "1"
                    self.assertEqual(getattr(t, field), getattr(t_bis2, field))

                if not isinstance(getattr(t_bis2, field), Type) \
                        and type(getattr(t_bis2, field)) is list \
                        and len(getattr(t_bis2, field)) > 0 \
                        and isinstance(getattr(t_bis2, field)[0], Property):
                    # ToDo: Change the way to do it without z and h
                    # Deserialized assertions for Property params for t_bis2
                    print "F", field, "2"
                    z = 0
                    for x in getattr(t_bis2, field):
                        print '\ncheck properties'
                        h = 0
                        for y in getattr(t, field):
                            if z == h:

                                prop_bool, st_prop = baseclass.ManagementObject.prop_equal(x, y)
                                self.assertTrue(prop_bool)
                                print "\nproperties fields not set:"
                                for st in st_prop:
                                    print st, "\n"
                            h += 1
                        z += 1

                if field == "operations" and getattr(t_bis2, field) is not None:
                    # Deserialized assertion for Operation params for t_bis2
                    print "F", field, "3"
                    # ToDo: Change the way to do it without z and h
                    z = 0
                    for x in getattr(t, field):
                        print '\ncheck operations'
                        h = 0
                        for y in getattr(t_bis2, field):
                            if z == h:

                                print '\ncheck types inside operations'
                                ct_bool, stt_list = baseclass.ManagementObject.type_equal(x.returnType, y.returnType)
                                self.assertTrue(ct_bool)
                                print "\ntype fields not set:"
                                for stt in stt_list:
                                    print stt, "\n"

                                op_bool, st_op = baseclass.ManagementObject.op_equal(x, y)

                                self.assertTrue(op_bool)
                                print "\noperation fields not set:"
                                for st in st_op:
                                    print st, "\n"
                            h += 1
                        z += 1

"""
    def test_serialization_with_nulls(self):
        mfc = MetaClassFactory(namespace="classTest", responsible_account="registrator")

        mfc.add_class(TestClass)

        for t in mfc.classes:
            
            for n in self.nullable_fields:
                del self.params[n]
                self.assertIsNone(getattr(t, n, None))
                s = BytesIO()

                t.serialize(s)
                serialization_size = s.tell()
                s.write('EOF')  # sentinel that should not be read by deserialization
                s.seek(0)
                t_bis = t.deserialize(s)
                self.assertEqual(serialization_size, s.tell(),
                                 "Deserialization has consumed less bytes than serialization")
"""

# ToDo: Complete with the serialization_with_nulls and args tests

if __name__ == '__main__':
    unittest.main()
