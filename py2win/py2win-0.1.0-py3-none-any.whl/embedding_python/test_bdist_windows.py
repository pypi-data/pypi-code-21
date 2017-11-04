#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import sys
import shutil
import subprocess

# Third party modules.

# Local modules.

# Globals and constants variables.

class Testbdist_windows(unittest.TestCase):

    def setUp(self):
        super().setUp()

        # Copy bdist_windows.py to sampleproject folder
        basedir = os.path.dirname(__file__)
        srcfilepath = os.path.join(basedir, 'bdist_windows.py')
        self.sampleproject_dirpath = os.path.join(basedir, 'testdata', 'sampleproject')
        shutil.copy(srcfilepath, self.sampleproject_dirpath)

    def tearDown(self):
        super().tearDown()
        os.remove(os.path.join(self.sampleproject_dirpath, 'bdist_windows.py'))

    def testbdist_windows(self):
        args = [sys.executable, 'setup.py', 'bdist_windows']
        cwd = self.sampleproject_dirpath
        subprocess.run(args, cwd=cwd, check=True)

        distdir = os.path.join(self.sampleproject_dirpath, 'dist', 'sample-1.2.0')
        self.assertTrue(os.path.exists(os.path.join(distdir, 'sample-console.exe')))
        self.assertTrue(os.path.exists(os.path.join(distdir, 'sample-gui.exe')))

        args = [os.path.join(distdir, 'sample-console.exe')]
        out = subprocess.run(args, cwd=distdir, check=True, stdout=subprocess.PIPE)
        self.assertEqual(b'Hello world', out.stdout.strip())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
