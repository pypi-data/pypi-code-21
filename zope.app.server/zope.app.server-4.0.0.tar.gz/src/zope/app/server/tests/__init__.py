import sys
from contextlib import contextmanager
from io import StringIO, BytesIO


# By using io.BytesIO() instead of cStringIO.StringIO() on Python 2 we make
# sure we're not trying to accidentally print unicode to stdout/stderr.
NativeStringIO = BytesIO if str is bytes else StringIO


@contextmanager
def capture_output(stdout=None, stderr=None):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout = stdout or NativeStringIO()
    sys.stderr = stderr = stderr or NativeStringIO()
    try:
        yield stdout, stderr
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
