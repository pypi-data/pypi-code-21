import sys
import unittest
from dativatools.s3_lib import S3Lib
from dativatools.log import Logger


class test_s3_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform testing of files upload/download from s3 bucket.
    '''

    config_dict = {'credentials': {'aws_access_key_id_optional': '',
                                   'aws_secret_access_key_optional': '',
                                   'bucket_name': '',
                                   'source_path': '../',
                                   'destination_path_optional': '',
                                   'environment_variables': 'no',
                                   'profile_name_optional': '',
                                   'function': 's3_upload',
                                   'log_file_path': 'log/',
                                   'log_file_name': 's3_valadation.txt'}}
    logger = Logger()
    logger_obj = logger.__get_logger__(config_dict['credentials']['log_file_path'], config_dict['credentials']['log_file_name'])

    # -------------------------------------------------------------------------
    #    Name: test_get_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test files and / or directories
    #          are received using rsync.
    # -------------------------------------------------------------------------
    def test_get_all(self):
        obj, con = self.get_s3_val_obj()
        result = obj.get_all(con, self.config_dict)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_put_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test that files and / or directories are send
    #          using rsync.
    # -------------------------------------------------------------------------
    def test_put_all(self):
        obj, con = self.get_s3_val_obj()
        file_list = obj.check_path_exists(self.config_dict['credentials']['destination_path_optional'])[1]
        result = obj.put_all(con, self.config_dict, file_list)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: get_s3_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------
    def get_s3_val_obj(self):
        obj = S3Lib(self.config_dict, logger_obj=self.logger_obj)
        con = obj.get_connection(self.config_dict)[2]
        return obj, con


'''
This function is used to initialize the test run
'''

if __name__ == '__main__':
        unittest.main()
