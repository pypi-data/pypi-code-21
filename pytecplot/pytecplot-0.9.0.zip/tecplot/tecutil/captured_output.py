import os
import sys

from contextlib import contextmanager
from io import TextIOWrapper, UnsupportedOperation
from tempfile import TemporaryFile

try:
    import ctypes
    import platform
    from ctypes.util import find_library
    if platform.system() == 'Windows':
        from ctypes.util import find_msvcrt
        msvcrt = find_msvcrt()
        if msvcrt is not None:
            libc = ctypes.cdll[msvcrt]
        else:
            libc = ctypes.cdll.msvcrt
    elif platform.system() in ['Mac', 'Darwin']:
        libc = ctypes.CDLL(find_library('c'))
    else: # if platform.system() in ['Linux']:
        libc = ctypes.CDLL(None)
except ImportError: # pragma: no cover
    libc = None


@contextmanager
def captured_output(out=os.devnull, err=None, mode='wb', errmode=None):

    if platform.system() == 'Windows':
        yield
        return

    err = out if err is None else err
    errmode = mode if errmode is None else errmode

    def open_stream(target):
        try:
            stream = open(target, mode)
            fd = stream.fileno()
            istemp = True
            isbuff = False
        except TypeError:
            try:
                fd = target.fileno()
                stream = target
                istemp = False
                isbuff = False
            except (AttributeError, UnsupportedOperation):
                stream = TemporaryFile(mode='w+b')
                fd = stream.fileno()
                istemp = True
                isbuff = True
        return stream, fd, istemp, isbuff

    try:
        # flush all output streams
        if libc is not None:
            libc.fflush(None)

        if (sys.stdout is not None) and (out is not None):
            ### stdout
            redirected_stdout = sys.stdout is not sys.__stdout__
            # save previous output stream
            _sys_stdout = sys.__stdout__
            _sys_stdout_fd = _sys_stdout.fileno()
            _sys_stdout_fd_dup = os.dup(_sys_stdout_fd)
            # flush pending output
            _sys_stdout.flush()
            if redirected_stdout:
                sys.stdout.flush()
            out_stream, out_fd, out_istemp, out_isbuff = open_stream(out)
            # overwrite file objects and low-level file descriptors
            os.dup2(out_fd, _sys_stdout_fd)
            if redirected_stdout:
                _saved_stdout = sys.stdout
                sys.stdout = os.fdopen(os.dup(out_fd),'wb')
                if sys.version_info >= (3,):
                    sys.stdout = TextIOWrapper(sys.stdout)

        if (sys.stderr is not None) and (err is not None):
            ### stderr
            redirected_stderr = sys.stderr is not sys.__stderr__
            # save previous output stream
            _sys_stderr = sys.__stderr__
            _sys_stderr_fd = _sys_stderr.fileno()
            _sys_stderr_fd_dup = os.dup(_sys_stderr_fd)
            # flush pending output
            _sys_stderr.flush()
            if redirected_stderr:
                sys.stderr.flush()
            if err is out:
                err_stream,err_fd,err_istemp,err_isbuff = out_stream,out_fd,False,False
            else:
                err_stream,err_fd,err_istemp,err_isbuff = open_stream(err)
            # overwrite file objects and low-level file descriptors
            os.dup2(err_fd, _sys_stderr_fd)
            if redirected_stderr:
                _saved_stderr = sys.stderr
                sys.stderr = os.fdopen(os.dup(err_fd),'wb')
                if sys.version_info >= (3,):
                    sys.stderr = TextIOWrapper(sys.stderr)

    finally:
        try:
            yield

        finally:

            # flush all output streams
            if libc is not None:
                libc.fflush(None)

            if (sys.stdout is not None) and (out is not None):
                ### restore stdout
                _sys_stdout.flush()
                if redirected_stdout:
                    sys.stdout.flush()
                # restore original streams and file descriptors
                os.dup2(_sys_stdout_fd_dup, _sys_stdout_fd)
                if redirected_stdout:
                    sys.stdout.close()
                    sys.stdout = _saved_stdout
                else:
                    sys.stdout = _sys_stdout
                os.close(_sys_stdout_fd_dup)


            if (sys.stderr is not None) and (err is not None):
                ### restore stderr
                _sys_stderr.flush()
                if redirected_stderr:
                    sys.stderr.flush()
                # restore original streams and file descriptors
                os.dup2(_sys_stderr_fd_dup, _sys_stderr_fd)
                if redirected_stderr:
                    sys.stderr.close()
                    sys.stderr = _saved_stderr
                else:
                    sys.stderr = _sys_stderr
                os.close(_sys_stderr_fd_dup)


            if (sys.stdout is not None) and (out is not None):
                if out_isbuff:
                    out_stream.seek(0)
                    out_bytes = out_stream.read()
                    if len(out_bytes):
                        try:
                            out.write(out_bytes)
                        except:
                            out_str = out_bytes.decode().strip()
                            try:
                                out.write(out_str)
                            except:
                                out_msg = 'captured output:\n{0}'.format('  '+out_str.replace('\n','\n  '))
                                out(out_msg)

                if out_istemp:
                    out_stream.close()

            if (sys.stderr is not None) and (err is not None):
                if err is not out:
                    if err_isbuff:
                        err_stream.seek(0)
                        err_bytes = err_stream.read()
                        if len(err_bytes):
                            try:
                                err.write(err_bytes)
                            except:
                                err_str = err_bytes.decode().strip()
                                try:
                                    err.write(err_str)
                                except:
                                    err_msg = 'captured output:\n{0}'.format('  '+err_str.replace('\n','\n  '))
                                    err(err_msg)

                    if err_istemp:
                        err_stream.close()


if sys.version_info < (3,3):

    '''
    This allows the contextmanager captured_output
    to be used as a decorator as well as a
    context. (This is already included in Py 3.3+)
    '''

    _captured_output = captured_output

    class captured_output(object):

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self._cm = _captured_output

        def __enter__(self, *args, **kwargs):
            self.cm = self._cm(*self.args,**self.kwargs)
            return self.cm.__enter__(*args, **kwargs)

        def __exit__(self, *args, **kwargs):
            return self.cm.__exit__(*args, **kwargs)

        def __call__(self, func):
            def wrapper(*args, **kwargs):
                with self._cm(*self.args,**self.kwargs):
                    return func(*args, **kwargs)
            return wrapper
