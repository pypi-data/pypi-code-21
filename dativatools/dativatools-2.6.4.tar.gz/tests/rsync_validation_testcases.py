import unittest
from dativatools.log import Logger
from dativatools.rsync_lib import RsyncLib


class test_rsync_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform testing of files and / or directories transfer using rsync.
    '''

    # -------------------------------------------------------------------------
    #    Name: test_get_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test files and / or directories
    #          are received using rsync.
    # -------------------------------------------------------------------------
    def test_get(self):
        get_settings = self.get_rsync_val_obj()
        obj = RsyncLib('log/', "rsync_valadation.txt")
        result = obj.get(get_settings[0])
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: test_put_all()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test that files and / or directories are send
    #          using rsync.
    # -------------------------------------------------------------------------
    def test_put(self):
        put_settings = self.get_rsync_val_obj()
        obj = RsyncLib('log/', "rsync_valadation.txt")
        result = obj.put(put_settings[1])
        self.assertTrue(result[0], True)

    # -------------------------------------------------------------------------
    #    Name: get_rsync_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------

    def get_rsync_val_obj(self):
        get_settings = {'source_path': '',              # Source path
                        'remote_host': '',              # Remote hostname
                        'destination_path': '',         # Destination path 
                        'options_optional': '',         # Rsync options
                        'password_optional': ''}        # Password if any
        put_settings = {'source_path': '',
                        'remote_host': '',
                        'destination_path': '/',
                        'options_optional': '',
                        'password_optional': ''}
        return get_settings, put_settings


'''
This function is used to initialize the test run
'''
if __name__ == '__main__':
        unittest.main()
