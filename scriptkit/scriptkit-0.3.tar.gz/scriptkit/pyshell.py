"""
Module Docstring
"""

__author__ = '"Your Name"'
__version__ = "0.1.0"
__license__ = "MIT"

import subprocess
from functools import partial


class PyShell:

    pipe_ctx = None
    last_process_output = None

    def __init__(self):
        self.pipe_ctx = PipeContextManager()

    def pipe(self):
        return self.pipe_ctx

    def _run(self, *args, **kwargs):

        input_value = None
        if self.pipe_ctx.is_piping:
            input_value = self.last_process_output

        completed_process = subprocess.run(
            args,
            input=input_value,
            stdout=subprocess.PIPE
        )

        self.last_process_output = completed_process.stdout

        return PyShellResult(completed_process)

    def __getattr__(self, name):
        return partial(self._run, name)


class PyShellResult:

    def __init__(self, completed_process):
        self.completed_process = completed_process

    @property
    def text(self):
        return self.stdout.decode('utf-8')

    @property
    def lines(self):
        return self.text.split('\n')

    def __iter__(self):
        for line in self.lines:
            yield line

    def __getattr__(self, name):
        return getattr(self.completed_process, name)


class PipeContextManager:

    is_piping = False

    def __enter__(self):
        self.is_piping = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.is_piping = False
