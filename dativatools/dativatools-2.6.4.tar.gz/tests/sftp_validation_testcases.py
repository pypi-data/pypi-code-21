import sys
import unittest
from dativatools.log import Logger
from dativatools.sftp_lib import SFTPLib


class test_sftp_validation(unittest.TestCase):
    '''
    Class to perform testing of upload and download of files
    through sftp server.
    '''

    # -------------------------------------------------------------------------
    #    Name: test_get_delta()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test that we are able get all 
    #          the files and directories in it from sftp server which 
    #          are having modified time as per delta
    # -------------------------------------------------------------------------
    def test_get_delta(self):
        settings = self.get_sftp_val_obj()
        obj = SFTPLib('log/', "sfpt_valadation.txt")
        result = obj.get_delta(settings)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_get_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test that we are able get all
    #          the files and directories in it from sftp server.
    # -------------------------------------------------------------------------
    def test_get(self):
        settings = self.get_sftp_val_obj()
        obj = SFTPLib('log/', "sfpt_valadation.txt")
        result = obj.get(settings)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_put_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test that we are able upload files and 
    #          / or directories to sftp server
    # -------------------------------------------------------------------------
    def test_put(self):
        settings = self.get_sftp_val_obj()
        obj = SFTPLib('log/', "sfpt_valadation.txt")
        result = obj.put(settings)
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: get_sftp_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------
    def get_sftp_val_obj(self):
        settings = {'credentials': {'remote_host': '',               # sftp host name
                                    'user': '',                      # sftp username
                                    'password_optional': '',         # Password if any
                                    'private_key_optional': '',      # Secret key if used for loging
                                    'key_phrase_optional': '',       # Key phrase if secret key is protected
                                    'is_protected_optional': ''},    # Is secret key protected
                    'get':         {'source_path': '',               # source path on sftp
                                    'destination_path': '',          # destination path to download data
                                    'days_optional': '1',            
                                    'hours_optional': '0',          
                                    'recursive': 'yes'},
                    'put':         {'destination_path': '',          # Destination path on sftp server
                                    'source_path': '',               # source path
                                    'recursive': 'yes'}}
        return settings


'''
This function is used to initialize the test run
'''
if __name__ == '__main__':
        unittest.main()
