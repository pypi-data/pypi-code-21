import unittest
import sys
from dativatools.log import Logger
from dativatools.data_validation import DataValidation



class test_data_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform testing data validations.
    '''

    # -------------------------------------------------------------------------
    #    Name: test_check_name()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if the files with the expected
    #          filenames are present in the specified directory.
    # -------------------------------------------------------------------------
    def test_check_name(self):
        obj = self.get_data_val_obj()
        result = obj.check_name()
        self.assertTrue(result, True)

    # -------------------------------------------------------------------------
    #    Name: test_check_extra_files()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if any extra files are present.
    # -------------------------------------------------------------------------
    def test_check_extra_files(self):
        obj = self.get_data_val_obj()
        result = obj.check_extra_files()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_date()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if that date is within the
    #          expected daterange.
    # -------------------------------------------------------------------------
    def test_check_date(self):
        obj = self.get_data_val_obj()
        result = obj.check_date()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_size()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if their sizesi of files fall
    #          within the prescribed thresholds.
    # -------------------------------------------------------------------------
    def test_check_size(self):
        obj = self.get_data_val_obj()
        result = obj.check_size()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_file_count()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if the count of files fall
    #          within the prescribed thresholds.
    # -------------------------------------------------------------------------
    def test_check_file_count(self):
        obj = self.get_data_val_obj()
        result = obj.check_file_count()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_file_extension()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test if the extension mathches
    #          the expected extension.
    # -------------------------------------------------------------------------
    def test_check_file_extension(self):
        obj = self.get_data_val_obj()
        result = obj.check_file_extension()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: get_data_val_obj()
    #    Returns: obj
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------
    def get_data_val_obj(self):
        config_dict = {'Programme': {'date_range': [-3, -1],
                                     'expected_extension': '.xml',
                                     'expected_filenames': 'PRG_*',
                                     'file_count_threshold': [500, 1000],
                                     'max_sizes': [119351],
                                     'min_sizes': [586],
                                     'other_expected_files': [],
                                     'path': 'sampledata/programme',
                                     'processing_date': '20170628',
                                     'date_format': '%Y%m%d'}}

        obj = DataValidation(config_dict[self.section], 'log/', "data_valadation.txt")
        return obj


'''
This function is used to initialize the test run and get the parameter
'''
if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_data_validation.section = sys.argv.pop()
        unittest.main()
