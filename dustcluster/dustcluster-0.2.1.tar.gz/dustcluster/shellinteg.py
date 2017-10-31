import subprocess
import sys
import os
import threading
import time
import logging


class ShellExecutorThread(threading.Thread):

    def __init__(self, read_file, cmd):
        self.readfrom = read_file
        self.proc = None
        self.cmd = cmd
        super(ShellExecutorThread, self).__init__()

    def run(self):
        self.proc = subprocess.Popen(self.cmd, stdin=self.readfrom, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, shell=True)
        self.proc.wait()


class ShellPipeOperation(object):

    def __init__(self):

        r, w = os.pipe()
        self.pipe_write_file = os.fdopen(w, 'w')
        self.pipe_read_file  = os.fdopen(r, 'r')
        self.old_stdout = None
        self.old_stderr = None
        self.tgt = None

    def invoke_shell_cmd(self, cmd):
        ''' 
            invokes a shell command in its own thread and pipes stdout to it 
            returns when proc is spawned
        '''

        self.tgt = ShellExecutorThread(self.pipe_read_file, cmd)
        self.tgt.start()

        while not self.tgt.proc:
            time.sleep(0.2)

    def redirect_stdout_to_shell(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.pipe_write_file
        sys.stderr = self.pipe_write_file

    def reset_stdout(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def get_shell_output(self):
        out, err = self.tgt.proc.communicate()
        return out, err

    def cleanup(self):
        self.pipe_write_file.close()
        self.tgt.join()

