import unittest
from dativatools.log import Logger
from dativatools.archive_manager import ArchiveManager

class test_archive_testcases(unittest.TestCase):
    '''
    Class to perform testing of archiving and unarchiving of files.
    '''

    # -------------------------------------------------------------------------
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test unarchive functionality works as expected
    # -------------------------------------------------------------------------
    def test_extract(self):
        # source_path : Path where archive exists
        # destination_path : Path to unarchive source file
        # extension : Archive format
        obj = ArchiveManager('log/', 'archive_mgr_validate.txt')
        result = obj.extract(source_path="sampledata/PostCommercial.tgz", destination_path="sampledata/", extension="tgz")
        self.assertTrue(result, True)

    # -------------------------------------------------------------------------
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is used to test archive files of from the source path
    # -------------------------------------------------------------------------
    def test_archive(self):
        # source_path : Path where file(s) need to be archived
        # destination_path : Path to generate archive file
        # archive_name : Name of archive
        # extension : Archive format
        obj = ArchiveManager('log/', 'archive_mgr_validate.txt')
        result = obj.archive(source_path="sampledata/PostCommercial", destination_path="sampledata/", archive_name="PostCommercial.tgz", extension="tgz")
        self.assertTrue(result, True)


'''
This function is used to initialize the test run
'''
if __name__ == '__main__':
    unittest.main()
