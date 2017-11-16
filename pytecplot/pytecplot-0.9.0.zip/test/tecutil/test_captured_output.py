from __future__ import print_function

import os
import sys
import logging
import platform
import unittest

from contextlib import contextmanager
from ctypes import c_void_p
from io import BytesIO
from tempfile import NamedTemporaryFile

from tecplot.tecutil import captured_output
from tecplot.tecutil.captured_output import libc

@contextmanager
def temporary_file(test_class,msg):
    f = NamedTemporaryFile(delete=False)
    fname = f.name
    f.close()
    yield fname
    with open(fname,'rb') as f:
        test_class.assertEqual(msg, f.read().decode().rstrip())
    os.remove(fname)

@contextmanager
def temporary_log(test_class,msg):
    logmsg = 'captured output:\n{0}'.format('  '+msg.replace('\n','\n  '))
    with temporary_file(test_class,logmsg) as fname:
        log = logging.getLogger('testmodule')
        log.addHandler(logging.FileHandler(fname))
        yield log

class TestCaptureDectoratorStdoutPrint(unittest.TestCase):

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(f):
                msg = 'context print to devnull'
                @captured_output(os.devnull)
                def print_stuff():
                    print(msg)
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(fname)
            def print_stuff():
                print(msg)
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(fstream)
                def print_stuff():
                    print(msg)
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(log.warning)
            def print_stuff():
                print(msg)
            print_stuff()

class TestCaptureDectoratorStdoutPuts(unittest.TestCase):

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(f):
                msg = 'context print to devnull'
                @captured_output(os.devnull)
                def print_stuff():
                    libc.puts(msg.encode())
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(fname)
            def print_stuff():
                libc.puts(msg.encode())
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(fstream)
                def print_stuff():
                    libc.puts(msg.encode())
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(log.warning)
            def print_stuff():
                libc.puts(msg.encode())
            print_stuff()

class TestCaptureDectoratorStdoutEcho(unittest.TestCase):

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(f):
                msg = 'context print to devnull'
                @captured_output(os.devnull)
                def print_stuff():
                    os.system('echo '+msg)
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(fname)
            def print_stuff():
                os.system('echo '+msg)
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(fstream)
                def print_stuff():
                    os.system('echo '+msg)
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(log.warning)
            def print_stuff():
                os.system('echo '+msg)
            print_stuff()

class TestCaptureDectoratorStdoutNotRedirectedPrint(unittest.TestCase):

    def test_print(self):
        msg = 'context print to sys stdout'
        saved_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            with temporary_file(self,msg) as fname:
                @captured_output(fname)
                def print_stuff():
                    print(msg)
                print_stuff()
        finally:
            sys.stdout = saved_stdout

class TestCaptureDectoratorStderrPrint(unittest.TestCase):

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(sys.stdout, f):
                msg = 'context print to devnull'
                @captured_output(sys.stdout, os.devnull)
                def print_stuff():
                    print(msg, file=sys.stderr)
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(sys.stdout, fname)
            def print_stuff():
                print(msg, file=sys.stderr)
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(sys.stdout, fstream)
                def print_stuff():
                    print(msg, file=sys.stderr)
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(sys.stdout, log.warning)
            def print_stuff():
                print(msg, file=sys.stderr)
            print_stuff()

class TestCaptureDectoratorStderrPuts(unittest.TestCase):
    def setUp(self):
        if platform.system() == 'Windows':
            self.libc_stderr = libc._get_osfhandle(2)
        elif platform.system() in ['Mac', 'Darwin']:
            self.libc_stderr = c_void_p.in_dll(libc, '__stderrp')
        else: # if platform.system() == 'Linux':
            self.libc_stderr = c_void_p.in_dll(libc, "stderr")

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(sys.stdout, f):
                msg = 'context print to devnull'
                @captured_output(sys.stdout, os.devnull)
                def print_stuff():
                    libc.fputs(msg.encode(),self.libc_stderr)
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(sys.stdout, fname)
            def print_stuff():
                libc.fputs(msg.encode(),self.libc_stderr)
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(sys.stdout, fstream)
                def print_stuff():
                    libc.fputs(msg.encode(),self.libc_stderr)
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(sys.stdout, log.warning)
            def print_stuff():
                libc.fputs(msg.encode(),self.libc_stderr)
            print_stuff()

class TestCaptureDectoratorStderrEcho(unittest.TestCase):

    def test_devnull(self):
        with BytesIO() as f:
            with captured_output(sys.stdout, f):
                msg = 'context print to devnull'
                @captured_output(sys.stdout, os.devnull)
                def print_stuff():
                    os.system('echo '+msg+' 1>&2')
                print_stuff()
            self.assertEqual(f.getvalue().decode(), '')

    def test_file(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            @captured_output(sys.stdout, fname)
            def print_stuff():
                os.system('echo '+msg+' 1>&2')
            print_stuff()

    def test_filestream(self):
        msg = 'context print to file'
        with temporary_file(self,msg) as fname:
            with open(fname,'wb') as fstream:
                @captured_output(sys.stdout, fstream)
                def print_stuff():
                    os.system('echo '+msg+' 1>&2')
                print_stuff()

    def test_log(self):
        msg = 'context print to log'
        with temporary_log(self,msg) as log:
            @captured_output(sys.stdout, log.warning)
            def print_stuff():
                os.system('echo '+msg+' 1>&2')
            print_stuff()

class TestCaptureDectoratorStderrRedirectedPrint(unittest.TestCase):

    def test_filestream(self):
        saved_stderr = sys.stderr
        try:
            with temporary_file(self,'') as fname:
                with open(fname,'wb') as fstream_stderr:
                    sys.stderr = fstream_stderr
                    msg = 'context print to file'
                    with temporary_file(self,msg) as fstream:
                        @captured_output(sys.stdout, fstream)
                        def print_stuff():
                            os.system('echo '+msg+' 1>&2')
                        print_stuff()
        finally:
            sys.stderr = saved_stderr

if __name__ == '__main__':
    from .. import main
    main()
