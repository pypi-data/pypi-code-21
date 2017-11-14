import unittest
import subprocess

class TestCmd(unittest.TestCase):

    def test_help(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_1.py",
            "--help"
            ],
            shell=False
        )

if __name__ == '__main__':
    unittest.main()
