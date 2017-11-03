import unittest

from conversionutil import convert


class TestConvertStorageSize(unittest.TestCase):

    def setUp(self):
        self.fn = convert.convert_storage_size

    def tearDown(self):
        pass

    def si_asserts_from_bytes(self,
                              ipunit,
                              opunit,
                              power):

        pwr = 10 ** power

        self.assertEqual(self.fn(value=-2*pwr, units=ipunit, output_units=opunit), u'-2.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'0.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16*pwr, units=ipunit, output_units=opunit), u'16.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16.5*pwr, units=ipunit, output_units=opunit), u'16.5{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=999.99*pwr, units=ipunit, output_units=opunit), u'1000.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=2500*pwr, units=ipunit, output_units=opunit), u'2500.0{u}'.format(u=opunit))

    def iec_asserts_from_bytes(self,
                               ipunit,
                               opunit,
                               power):

        pwr = 2 ** power

        self.assertEqual(self.fn(value=-2*pwr, units=ipunit, output_units=opunit), u'-2.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'0.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16*pwr, units=ipunit, output_units=opunit), u'16.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16.5*pwr, units=ipunit, output_units=opunit), u'16.5{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=999.99*pwr, units=ipunit, output_units=opunit), u'1000.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=2500*pwr, units=ipunit, output_units=opunit), u'2500.0{u}'.format(u=opunit))

    def si_asserts_to_bytes(self,
                            ipunit,
                            opunit,
                            power):

        pwr = 10 ** power

        self.assertEqual(self.fn(value=-2, units=ipunit, output_units=opunit), u'-{v}{u}'.format(v=2*pwr,
                                                                                                 u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=0*pwr,
                                                                                               u=opunit))
        self.assertEqual(self.fn(value=16, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=16*pwr,
                                                                                                u=opunit))
        self.assertEqual(self.fn(value=16.5, units=ipunit, output_units=opunit), u'{v:.0f}{u}'.format(v=16.5*pwr,
                                                                                                      u=opunit))
        self.assertEqual(self.fn(value=999.99, units=ipunit, output_units=opunit), u'{v:.0f}{u}'.format(v=999.99*pwr,
                                                                                                        u=opunit))
        self.assertEqual(self.fn(value=2500, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=2500*pwr,
                                                                                                  u=opunit))

    def iec_asserts_to_bytes(self,
                             ipunit,
                             opunit,
                             power):

        pwr = 2 ** power

        self.assertEqual(self.fn(value=-2, units=ipunit, output_units=opunit), u'-{v}{u}'.format(v=2*pwr,
                                                                                                 u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=0*pwr,
                                                                                               u=opunit))
        self.assertEqual(self.fn(value=16, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=16*pwr,
                                                                                                u=opunit))
        self.assertEqual(self.fn(value=16.5, units=ipunit, output_units=opunit), u'{v:.0f}{u}'.format(v=16.5*pwr,
                                                                                                      u=opunit))
        self.assertEqual(self.fn(value=999.99, units=ipunit, output_units=opunit), u'{v:.0f}{u}'.format(v=999.99*pwr,
                                                                                                        u=opunit))
        self.assertEqual(self.fn(value=2500, units=ipunit, output_units=opunit), u'{v}{u}'.format(v=2500*pwr,
                                                                                                  u=opunit))

    # Test byte pass through
    def test_convert_storage_size_bytes_to_bytes(self):

        ipunit = opunit = u'B'
        self.assertEqual(self.fn(value=-2, units=ipunit, output_units=opunit), u'-2{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16, units=ipunit, output_units=opunit), u'16{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=999, units=ipunit, output_units=opunit), u'999{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=2500, units=ipunit, output_units=opunit), u'2500{u}'.format(u=opunit))

    # Test output conversion
    def test_convert_storage_size_bytes_to_kilobytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'KB', power=3)

    def test_convert_storage_size_bytes_to_megabytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'MB', power=6)

    def test_convert_storage_size_bytes_to_gigabytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'GB', power=9)

    def test_convert_storage_size_bytes_to_terabytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'TB', power=12)

    def test_convert_storage_size_bytes_to_petabytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'PB', power=15)

    def test_convert_storage_size_bytes_to_kibibytes(self):
        self.iec_asserts_from_bytes(ipunit=u'B', opunit=u'KiB', power=10)

    def test_convert_storage_size_bytes_to_mebibytes(self):
        self.iec_asserts_from_bytes(ipunit=u'B', opunit=u'MiB', power=20)

    def test_convert_storage_size_bytes_to_gibibytes(self):
        self.iec_asserts_from_bytes(ipunit=u'B', opunit=u'GiB', power=30)

    def test_convert_storage_size_bytes_to_tebibytes(self):
        self.iec_asserts_from_bytes(ipunit=u'B', opunit=u'TiB', power=40)

    def test_convert_storage_size_bytes_to_pebibytes(self):
        self.iec_asserts_from_bytes(ipunit=u'B', opunit=u'PiB', power=50)

    # Test input conversion
    def test_convert_storage_size_kilobytes_to_bytes(self):
        self.si_asserts_from_bytes(ipunit=u'B', opunit=u'KB', power=3)

    def test_convert_storage_size_megabytes_to_bytes(self):
        self.si_asserts_to_bytes(ipunit=u'MB', opunit=u'B', power=6)

    def test_convert_storage_size_gigabytes_to_bytes(self):
        self.si_asserts_to_bytes(ipunit=u'GB', opunit=u'B', power=9)

    def test_convert_storage_size_terabytes_to_bytes(self):
        self.si_asserts_to_bytes(ipunit=u'TB', opunit=u'B', power=12)

    def test_convert_storage_size_petabytes_to_bytes(self):
        self.si_asserts_to_bytes(ipunit=u'PB', opunit=u'B', power=15)

    def test_convert_storage_size_kibibytes_to_bytes(self):
        self.iec_asserts_to_bytes(ipunit=u'KiB', opunit=u'B', power=10)

    def test_convert_storage_size_mebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(ipunit=u'MiB', opunit=u'B', power=20)

    def test_convert_storage_size_gibibytes_to_bytes(self):
        self.iec_asserts_to_bytes(ipunit=u'GiB', opunit=u'B', power=30)

    def test_convert_storage_size_tebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(ipunit=u'TiB', opunit=u'B', power=40)

    def test_convert_storage_size_pebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(ipunit=u'PiB', opunit=u'B', power=50)

    # Test combined conversion
    def test_convert_storage_size_megabytes_to_gigabytes(self):

        pwr = 10 ** 3
        ipunit = u'MB'
        opunit = u'GB'

        self.assertEqual(self.fn(value=-2*pwr, units=ipunit, output_units=opunit), u'-2.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=0, units=ipunit, output_units=opunit), u'0.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16*pwr, units=ipunit, output_units=opunit), u'16.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=16.5*pwr, units=ipunit, output_units=opunit), u'16.5{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=999.99*pwr, units=ipunit, output_units=opunit), u'1000.0{u}'.format(u=opunit))
        self.assertEqual(self.fn(value=2500*pwr, units=ipunit, output_units=opunit), u'2500.0{u}'.format(u=opunit))

    # Test failure scenarios
    def test_convert_storage_size_invalid_input_unit(self):
        with self.assertRaises(ValueError):
            self.fn(value=10, units=u'A', output_units=u'B')

    def test_convert_storage_size_invalid_output_unit(self):
        with self.assertRaises(ValueError):
            self.fn(value=10, units=u'MB', output_units=u'A')

# TODO: Write these tests
class TestConvertToUnicode(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertDatetimeToEpoch(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertEpochToTime(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertGetConversion(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


if __name__ == u'__main__':
    unittest.main()
