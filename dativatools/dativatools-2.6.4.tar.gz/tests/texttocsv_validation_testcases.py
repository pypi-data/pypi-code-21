import sys
import unittest
from dativatools.log import Logger
from dativatools.txt_to_csv_converter import TextToCsvConverter
class test_txt_to_csv_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform validation testing on text to csv conversions
    '''
    config_dict = {"path": {"source_file": "../",
                            "destination_path": "../"},
                   "csv":  {"seperator": "|",
                            "headers_optional": "",
                            "update_header": "no"},
                   "txt":  {"file_seperator": "|",
                            "header_available_in_file": "yes",
                            "expected_headers_optional": "Channel, ChannelName, ServiceKey, HouseNo, Title, Series, SeriesNum, EpisodeNum, Category, ActualDuration, VersionType, AspectRatio, Subtitles, Rating, Genre, SubGenre, ActualStartDateTime, ActualEndDateTime, MediaId, Duration, Start, Language1, Language2,SubTitleLanguage, Blackout"},
                   "log": {"log_file_path": "log/",
                           "log_file_name": "txt_to_csv_val.txt"}}
    logger = Logger()
    logger_obj = logger.__get_logger__(config_dict['log']['log_file_path'], config_dict['log']['log_file_name'])
    # -------------------------------------------------------------------------
    #    Name: test_check_required_field_exists()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test required fields exists
    # -------------------------------------------------------------------------
    def test_check_required_field_exists(self):
        obj = self.get_txt_to_csv_val_obj()
        result = obj.check_required_field_exists()
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_file_exists()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test that file exists
    # -------------------------------------------------------------------------
    def test_check_file_exists(self):
        obj = self.get_txt_to_csv_val_obj()
        result = obj.file_exists(self.config_dict)[1]
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_file_size()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test file size
    # -------------------------------------------------------------------------
    def test_check_file_size(self):
        obj = self.get_txt_to_csv_val_obj()
        result = obj.verify_file_size(self.config_dict['txt'], self.config_dict['path']['source_file'])
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_check_columns_present()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test cloumns present
    # -------------------------------------------------------------------------
    def test_check_columns_present(self):
        obj = self.get_txt_to_csv_val_obj()
        file_header = obj.verify_file_size(self.config_dict['txt'], self.config_dict['path']['source_file'])
        result = obj.verify_columns_present(self.config_dict['txt']['expected_headers_optional'], file_header[2])
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_convert_text_to_csv()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test that text file is converted to csv
    # -------------------------------------------------------------------------
    def test_convert_text_to_csv(self):
        obj = self.get_txt_to_csv_val_obj()
        result = obj.convert(self.config_dict)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: get_txt_to_csv_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------

    def get_txt_to_csv_val_obj(self):
        obj = TextToCsvConverter(self.config_dict, self.logger_obj)
        return obj


'''
This function is used to initialize the test run
'''
if __name__ == '__main__':
        unittest.main()
