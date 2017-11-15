import sys
import os
import io
import subprocess
import signal
import codecs
import shlex

try:
    import selectors
    _HAS_SELECTORS = True
except ImportError:
    # Python3.3 does not have the selectors module
    _HAS_SELECTORS = False
    
from collections import namedtuple, deque

from . import config, tmpfiles

def backslashreplace_while_decoding (decoding_error):
    """Replacement for the backslashreplace error handler on Python <3.5."""

    # Before Python 3.5 the backslashreplace error handler could
    # only be used for encoding.
    # This is a version for decoding.
    if not isinstance(decoding_error, UnicodeDecodeError):
        raise TypeError('backslashreplace_while_decoding error handler can only be used for decoding')
    repl = '\\' + hex(decoding_error.object[decoding_error.start])[1:]
    return (repl, decoding_error.end)

# package-wide default encoding
# used for any format that does not explicitly override it
DEFAULTENCODING = 'utf-8'

# package-wide safe fallback encoding
# to be used if decoding input as utf-8 fails
FALLBACKENCODING = 'latin-1' \
                   if config.input_decoding == 'lenient' else \
                   'utf-8'

# vcf gets read in and written as utf-8
# handling of decoding errors during reading is determined by config setting
vcf_defaultencoding = 'utf-8' # see the official format specs
if config.input_decoding == 'lenient':
    if sys.version_info[:2] < (3, 5):
        # need replacement for backslashreplace error handler
        # for decoding with Python <3.5
        vcf_handle_decoding_errors = 'backslashreplace_while_decoding'
        codecs.register_error(vcf_handle_decoding_errors,
                              backslashreplace_while_decoding)
    else:
        vcf_handle_decoding_errors = 'backslashreplace'
else:
    vcf_handle_decoding_errors = 'strict'


def get_custom_std (stream, encoding=DEFAULTENCODING, errors=None):
    current_encoding = stream.encoding
    if encoding is None:
        encoding = current_encoding
    elif encoding != current_encoding:
        # see if the normalized names match
        encoding = codecs.lookup(encoding).name
        current_encoding = codecs.lookup(current_encoding).name
    if errors is None:
        errors = stream.errors
    ret_stream = stream
    if encoding != current_encoding or errors != stream.errors:
        try:
            ret_stream = CustomStd(stream, encoding, errors)
        except:
            pass
    return ret_stream


class CustomStd (io.TextIOWrapper):
    def __init__(self, stream, encoding, errors):
        self._super = super(CustomStd, self)
        self.original = stream
        self._super.__init__(stream.buffer,
                             encoding=encoding,
                             errors=errors,
                             newline=stream.newlines,
                             line_buffering=True)

    def write (self, data):
        self.original.flush()       
        self._super.write(data)

    def close (self):
        self._super.flush()


class RecordBasedFormatReader (object):
    def __init__ (self, ifile_obj, encoding=DEFAULTENCODING, errors=None):
        if ifile_obj is sys.stdin:
            self.ifo = get_custom_std(
                ifile_obj, encoding=encoding, errors=errors
                )
        else:
            self.ifo = ifile_obj
        try:
            self.ifo.seek(0)
        except:
            self.ifo_isseekable = False
        else:
            self.ifo_isseekable = True

    def raw_iter (self):
        for line in self.ifo:
            yield line

    def __iter__ (self):
        return self

    def __next__ (self):
        raise NotImplementedError
    
    def __enter__(self):
        return self

    def __exit__(self, *error_desc):
        self.close()

    def close (self):
        if self.ifo is not sys.stdin and hasattr(self.ifo, 'close'):
            self.ifo.close()


class RecordBasedFormatWriter (object):
    def __init__ (self, ofile_obj, encoding=DEFAULTENCODING, converter=None):
        if ofile_obj is sys.stdout:
            self.out = get_custom_std(ofile_obj, encoding=encoding)
        else:
            self.out = ofile_obj
        if converter is not None:
            header = converter.format_header()
            if header:
                self.out.write(header)
                self.out.write('\n')
            self.record_converter = converter.convert
        else:
            self.record_converter = str
        self.records_written = 0
        self.converter = converter
        
    def write (self, record):
        w = self.out.write(self.record_converter(record))
        w += self.out.write('\n')
        self.records_written += 1
        return w

    def finalize (self):
        if self.converter is not None:
            footer = self.converter.format_footer()
            if footer:
                self.out.write(footer)
                self.out.write('\n')
        
    def __enter__(self):
        return self

    def __exit__(self, *error_desc):
        self.finalize()
        self.close()

    def close (self):
        if self.out is not sys.stdout and hasattr(self.out, 'close'):
            self.out.close()


# just an idea:
# def get_safe_stdout (encoding=DEFAULTENCODING):
#     if encoding == sys.stdout.encoding:
#         return sys.stdout
#     else:
#         return SafeStdoutWriter()
#
#
# class SafeStdoutWriter (object):
#     def write (self, data):
#         encoding = sys.stdout.encoding
#         data = str(data.encode(encoding, 'backslashreplace'), encoding)
#         sys.stdout.write(data)

    
ApplicationReturnValue = namedtuple('ApplicationReturnValue', ['call', 'results', 'errors'])


class ExternalApplicationCall (object):
    """General interface for running wrapped applications as subprocesses."""

    def __init__ (self, command=None, subcommand=None, args=None,
                  stdin = None, stdout = None, stderr = None,
                  input = None, chunksize=32768):
        # argument validation
        if command is None:
            if subcommand is not None:
                raise MiModDLibraryError(
                    'The subcommand argument requires the command argument to '
                    'be specified.'
                    )
            elif args is None:
                raise MiModDLibraryError(
                    'Either the command or the args argument must be provided.'
                    )
        if input is not None and stdin is not subprocess.PIPE:
            raise MiModDLibraryError(
                'Cannot send data to a process without piping its stdin'
                )        

        # construct args list for Popen object
        if command is None:
            self.call_args = []
        else:
            self.call_args = [command]
            if subcommand is not None:
                self.call_args.append(subcommand)
        self.call_args += args

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        if input is None:
            self.bytes_input = None
        else:
            self.bytes_input = input.encode(DEFAULTENCODING)
        self.Popen = None
        self.chunksize = chunksize
        self._run_info = [None , None]
        self.run_info = None
        
    def start (self):
        self.Popen = subprocess.Popen(self.call_args,
                                      stdin=self.stdin,
                                      stdout=self.stdout,
                                      stderr=self.stderr)
        if self.stdout == subprocess.PIPE:
            self._run_info[0] = b''
        if self.stderr == subprocess.PIPE:
            self._run_info[1] = b''
        
    if _HAS_SELECTORS:
        # The following patches self.Popen.communicate for Python3.4+
        # to enable tail-like functionality for piped stdout and stderr
        # to prevent exceeding memory consumption when communicating with
        # very verbose applications
        # (see https://sourceforge.net/p/mimodd/tickets/97/).
        def communicate(self, timeout=None):
            """Interact with process: Send data to stdin.  Read data from
            stdout and stderr, until end-of-file is reached.  Wait for
            process to terminate.

            The optional "input" argument should be data to be sent to the
            child process (if self.universal_newlines is True, this should
            be a string; if it is False, "input" should be bytes), or
            None, if no data should be sent to the child.

            communicate() returns a tuple (stdout, stderr).  These will be
            bytes or, if self.universal_newlines was True, a string.
            """

            # Optimization: If we are not worried about timeouts, we haven't
            # started communicating, and we have one or zero pipes, using select()
            # or threads is unnecessary.
            if (timeout is None and not self.Popen._communication_started and
                [self.Popen.stdin, self.Popen.stdout, self.Popen.stderr]
                .count(None) >= 2):
                stdout = None
                stderr = None
                if self.Popen.stdin:
                    self.Popen.stdin.write(self.bytes_input)
                elif self.Popen.stdout:
                    self._run_info[0] = self._read(self.Popen.stdout)
                    self.Popen.stdout.close()
                elif self.Popen.stderr:
                    self._run_info[1] = self._read(self.Popen.stderr)
                    self.Popen.stderr.close()
                self.Popen.wait()
            else:
                if timeout is not None:
                    endtime = _time() + timeout
                else:
                    endtime = None
                try:
                    self._run_info[0], self._run_info[1] = self._communicate(
                        self.bytes_input, endtime, timeout
                        )
                finally:
                    self.Popen._communication_started = True

                sts = self.Popen.wait(timeout=self.Popen._remaining_time(endtime))

        def _read (self, fh):
            output = b'' # we're only dealing with byte streams
            data = fh.read(self.chunksize)
            while data:
                space_to_fill = self.chunksize-len(data)
                if output and space_to_fill > 0:
                    output = output[-space_to_fill:] + data
                else:
                    output = data
                data = fh.read(self.chunksize)
            return output
            
        def _communicate(self, input, endtime, orig_timeout):
            if self.Popen.stdin and not self.Popen._communication_started:
                # Flush stdio buffer.  This might block, if the user has
                # been writing to .stdin in an uncontrolled fashion.
                try:
                    self.Popen.stdin.flush()
                except BrokenPipeError:
                    pass  # communicate() must ignore BrokenPipeError.
                if not self.bytes_input:
                    try:
                        self.Popen.stdin.close()
                    except BrokenPipeError:
                        pass  # communicate() must ignore BrokenPipeError.

            stdout = None
            stderr = None

            # Only create this mapping if we haven't already.
            if not self.Popen._communication_started:
                self.Popen._fileobj2output = {}
                excess_bytes = {}
                if self.Popen.stdout:
                    self.Popen._fileobj2output[self.Popen.stdout] = deque()
                    excess_bytes[self.Popen.stdout] = -self.chunksize
                if self.Popen.stderr:
                    self.Popen._fileobj2output[self.Popen.stderr] = deque()
                    excess_bytes[self.Popen.stderr] = -self.chunksize
            if self.Popen.stdout:
                stdout = self.Popen._fileobj2output[self.Popen.stdout]
            if self.Popen.stderr:
                stderr = self.Popen._fileobj2output[self.Popen.stderr]

            self.Popen._save_input(input)

            if self.Popen._input:
                input_view = memoryview(self.Popen._input)

            with subprocess._PopenSelector() as selector:
                if self.Popen.stdin and input:
                    selector.register(self.Popen.stdin, selectors.EVENT_WRITE)
                if self.Popen.stdout:
                    selector.register(self.Popen.stdout, selectors.EVENT_READ)
                if self.Popen.stderr:
                    selector.register(self.Popen.stderr, selectors.EVENT_READ)

                while selector.get_map():
                    timeout = self.Popen._remaining_time(endtime)
                    if timeout is not None and timeout < 0:
                        raise TimeoutExpired(self.Popen.args, orig_timeout)

                    ready = selector.select(timeout)
                    self.Popen._check_timeout(endtime, orig_timeout)

                    # XXX Rewrite these to use non-blocking I/O on the file
                    # objects; they are no longer using C stdio!

                    for key, events in ready:
                        if key.fileobj is self.Popen.stdin:
                            chunk = input_view[self.Popen._input_offset :
                                               self.Popen._input_offset + subprocess._PIPE_BUF]
                            try:
                                self.Popen._input_offset += os.write(key.fd, chunk)
                            except BrokenPipeError:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            else:
                                if self.Popen._input_offset >= len(self.Popen._input):
                                    selector.unregister(key.fileobj)
                                    key.fileobj.close()
                        elif key.fileobj in (self.Popen.stdout, self.Popen.stderr):
                            data = os.read(key.fd, 32768)
                            if not data:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            else:
                                buffer = self.Popen._fileobj2output[key.fileobj]
                                buffer.append(data)
                                excess_bytes[key.fileobj] += len(data)
                                while excess_bytes[key.fileobj] > len(
                                    buffer[0]
                                    ):
                                    excess_bytes[key.fileobj] -= len(
                                        buffer.popleft()
                                        )

            self.Popen.wait(timeout=self.Popen._remaining_time(endtime))

            # All data exchanged.  Translate deques into strings.
            if stdout is not None:
                stdout = b''.join(stdout)
            if stderr is not None:
                stderr = b''.join(stderr)

            return (stdout, stderr)

    else:
        # fall back to unpatched subprocess.Popen.communicate for Python3.3 
        def communicate (self):
            self._run_info[0], self._run_info[1] = self.Popen.communicate(
                self.bytes_input
                )

    def wait (self):
        self.Popen.wait()
        if self._run_info[0] is not None:
            self._run_info[0] += self._read(self.Popen.stdout)
        if self._run_info[1] is not None:
            self._run_info[1] += self._read(self.Popen.stderr)
        return self.finalize()
        
    def finalize (self):
        _results, _errors = self._run_info
        if _results is not None:
            try:
                results = _results.decode(DEFAULTENCODING)
            except UnicodeDecodeError:
                results = _results.decode(FALLBACKENCODING)
            results = results.replace('\r\n', '\n').replace('\r', '\n')
        else:
            results = _results
        if _errors is not None:
            try:
                errors = _errors.decode(DEFAULTENCODING)
            except UnicodeDecodeError:
                errors = _errors.decode(FALLBACKENCODING)
            errors = errors.replace('\r\n', '\n').replace('\r', '\n')
        else:
            errors = _errors

        self.run_info = ApplicationReturnValue(
            ' '.join(shlex.quote(arg) for arg in self.call_args),
            results,
            errors)
        return self.Popen.returncode

    @tmpfiles.allow_cleanup_on_sigterm
    def run (self, start=True):
        # catch SIGTERM so that we can also terminate the subprocess
        try:
            if start:
                self.start()
            self.communicate()
        except:
            # terminate the subprocess
            try:
                self.Popen.terminate()
            except:
                pass
            raise
        return self.finalize()
