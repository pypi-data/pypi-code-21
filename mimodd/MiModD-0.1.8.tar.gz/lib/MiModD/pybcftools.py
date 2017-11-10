import subprocess
import io
import gzip

from .encoding_base import vcf_defaultencoding as defaultencoding
from .encoding_base import vcf_handle_decoding_errors as handle_decoding_errors

from . import config
from . import FormatParseError


class bcfViewer (object):
    def __init__ (self, ifile, encoding=defaultencoding,
                  errors=handle_decoding_errors):
        self.ifile = ifile
        self.encoding = encoding
        self.errors = errors
        call = [config.bcftools_exe, 'view', ifile]
        self.subprocess = subprocess.Popen(call,
                          stdout = subprocess.PIPE)
        self.stream = self.subprocess.stdout

    def __iter__ (self):
        return self

    def __next__ (self):
        return next(self.stream).decode(self.encoding, self.errors)

    def readline (self):
        return self.stream.readline().decode(self.encoding, self.errors)

    def close (self):
        self.stream.close()

    
def view (ifile, encoding=defaultencoding, errors=handle_decoding_errors):
    return bcfViewer(ifile)


class bcfHeader (object):
    def __init__ (self, data):
        if isinstance(data, str):
            self.version = (2, 2)
            self.nul_byte = '\x00'
            self.lines = data.rstrip('\n').split('\n')
        else:
            if data.read(3) != b'BCF':
                raise FormatParseError('{0} does not seem to be a bcf file.'
                                       .format(fileobject.name))
            # parse two-byte version information as a tuple
            self.version = ord(data.read(1)), ord(data.read(1))
            # parse length of header text
            length = int.from_bytes(data.read(4), 'little')
            *self.lines, self.nul_byte = data.read(length).decode(defaultencoding,
                                                                  handle_decoding_errors
                                                                  ).split('\n')
            if self.nul_byte != '\x00'*len(self.nul_byte):
                raise FormatParseError(
                    'Expected BCF header to be NULL-terminated. \
Found "{0}" instead.'.format(token = self.nul_byte))
            self.line_iter = iter(self.lines)
            
    def readline (self):
        """Simple readline implementation for compatibility with pyvcf.Info."""
        
        try:
            line = next(self.line_iter)
        except StopIteration:
            line = ''
        return line
            
    def __bytes__ (self):
        ret = b'BCF'+bytes(self.version)
        vcf_header = '\n'.join(self.lines) + self.nul_byte
        vcf_header = vcf_header.encode(defaultencoding)
        ret += len(vcf_header).to_bytes(4, 'little')
        ret += vcf_header
        return ret

    
def open (ifile):
    bcf_magic_string = b'BCF'
    with gzip.open(ifile, 'rb') as f:
        try:
            if f.read(3) == bcf_magic_string:
                return gzip.open(ifile, 'rb')
        except (IOError, OSError):
            # An OSError at this level means that this is not a gzipped file.
            # We ignore the error here, but may raise a more appropriate
            # FormatParseError afterwards, if reading as a regular file also
            # fails.
            pass
    with io.open(ifile, 'rb') as f:
        if f.read(3) == bcf_magic_string:
            return io.open(ifile, 'rb')
    raise FormatParseError('{0} does not seem to be a bcf file.'.format(ifile))


def get_header (ifile):
    with open(ifile) as f:
        return bcfHeader(f)
