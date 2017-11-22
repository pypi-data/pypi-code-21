import os
import shutil
import unittest

from hgicommon.managers import TempManager


class TestTempManager(unittest.TestCase):
    """
    Tests for `TempManager`.
    """
    def setUp(self):
        default_kwargs = {"prefix": self.__class__.__name__}
        self.manager = TempManager(default_kwargs, default_kwargs)

    def tearDown(self):
        self.manager.tear_down()

    def test_tear_down_when_no_temps(self):
        self.manager.tear_down()

    def test_tear_down_when_deleted_temp(self):
        location = self.manager.create_temp_directory()
        assert os.path.exists(location)
        shutil.rmtree(location)
        assert not os.path.exists(location)
        self.manager.tear_down()

    def test_create_temp_directory(self):
        location = self.manager.create_temp_directory()
        self.assertFalse(os.path.isfile(location))
        self.assertTrue(os.access(location, os.W_OK))
        self.assertTrue(os.access(location, os.R_OK))

    def test_create_temp_directory_using_kwargs(self):
        prefix = "testprefix"
        location = self.manager.create_temp_directory(prefix=prefix)
        self.assertTrue(os.path.basename(location).startswith(prefix))

    def test_create_temp_file(self):
        _, location = self.manager.create_temp_file()
        self.assertTrue(os.path.isfile(location))
        self.assertTrue(os.access(location, os.W_OK))
        self.assertTrue(os.access(location, os.R_OK))

    def test_create_temp_file_using_kwargs(self):
        prefix = "testprefix"
        _, location = self.manager.create_temp_file(prefix=prefix)
        self.assertTrue(os.path.basename(location).startswith(prefix))

    def test_create_temp_file_file_handle(self):
        handle, location = self.manager.create_temp_file(text=True)
        data = "testing"
        os.write(handle, bytes(data, "utf8"))
        with open(location, "r") as file:
            self.assertEqual(data, file.read())


if __name__ == "__main__":
    unittest.main()
