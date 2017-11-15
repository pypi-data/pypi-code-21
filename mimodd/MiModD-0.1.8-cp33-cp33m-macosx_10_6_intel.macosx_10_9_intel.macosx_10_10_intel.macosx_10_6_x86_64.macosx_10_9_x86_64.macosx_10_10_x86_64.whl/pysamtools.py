"""A collection of wrappers that provide a functional programming interface
to the csamtools software suite."""

import subprocess
import glob
import sys
import os
import signal
import tempfile
import gzip
import io
import struct
import shutil

from collections import namedtuple

from . import config, tmpfiles, encoding_base
from . import SamtoolsRuntimeError, ArgumentParseError, FormatParseError

from .encoding_base import DEFAULTENCODING, FALLBACKENCODING
from .encoding_base import ExternalApplicationCall, ApplicationReturnValue


SamtoolsReturnValue = namedtuple('SamtoolsReturnValue', ['call', 'results', 'errors'])


class SamtoolsCall (ExternalApplicationCall):
    """Object representation of a samtools subcommand call.

    Used by all samtools wrappers in pysamtools.
    """


    def __init__ (self, subcommand, args,
                  stdin = None, stdout = None, stderr = None,
                  input = None):
        super(SamtoolsCall, self).__init__(command=config.samtools_exe,
                                           subcommand=subcommand,
                                           args=args,
                                           stdin=stdin,
                                           stdout=stdout,
                                           stderr=stderr,
                                           input=input)
        
    def run (self, start=True):
        returncode = super(SamtoolsCall, self).run(start)
        self.run_info = SamtoolsReturnValue(self.run_info.call,
                                            self.run_info.results,
                                            self.run_info.errors)
        return returncode

    
def _get_bgzf_cdata_size (bgzf_block):
    """Parses the header of BGZF input.

    Returns the length of the following compressed data section
    if succesful. Raises a FormatParseError otherwise."""
    
    e = FormatParseError()
    magic = bgzf_block.read(2)

    if magic == b'':
        e.msg = 'Empty input'
        raise e
    
    if magic != b'\037\213':
        # not a gzipped file
        raise e

    try:
        method, flag, mtime, xlen = struct.unpack("<BBIxxH",
                                                  bgzf_block.read(10))
    except struct.error:
        # truncated input
        raise e
    if method != 8 or flag != 4:
        # not a bgzf file
        raise e

    extras_read = 0
    while extras_read < xlen:
        try:
            si1, si2, slen = struct.unpack('<BBH', bgzf_block.read(4))
        except struct.error:
            # truncated input
            raise e
        scontent = bgzf_block.read(slen)
        if len(scontent) != slen:
            # truncated input
            raise e
        if si1 == 66 and si2 == 67 and slen == 2:
            cdata_size = int.from_bytes(scontent, 'little') - xlen - 19
            if cdata_size < 0:
                raise e
            return cdata_size
        extras_read += 4 + slen
    # not a bgzf file
    raise e


def is_bam (ifile):
    """Determine whether the content of ifile has a BAM format signature.

    ifile can be a filename or an existing binary file object."""
 
    if isinstance(ifile, str):
        ifile = open(ifile, 'rb')
        needs_close = True
    else:
        needs_close = False

    try:
        f = io.BytesIO(ifile.read(256))
        try:
            # see if we can parse the input header as BGZF
            _ = _get_bgzf_cdata_size(f)
        except FormatParseError:
            return False
        # ok, there is a BGZF header
        # now rewind and parse the input with gzip
        # to see if cdata starts with the BAM format magic string
        # gzip.open could be used instead of gzip.GzipFile.
        f.seek(0)
        with gzip.GzipFile(fileobj=f) as g:
            try:
                return g.read(4) == b'BAM\1'
            except (IOError, OSError):
                # this isn't even a gzipped file
                return False
    finally:
        # TO DO: switch to using an ExitStack
        if needs_close:
            ifile.close()
            
            
class header (object):
    """A pure Python replacement for samtools view -H.

    Implemented as an iterator over the header lines of a sam/bam file.

    ifile must be a file name or '-' to read from stdin.
    When iformat is 'sam' or 'bam', the format of ifile is verified
    (samtools-0.1.x behavior), but when it is None, the format of the input
    gets autodetected (samtools-1.x behavior)."""

    def __init__ (self, ifile, iformat = None):
        # sanitize parameters
        if iformat not in ('sam', 'bam', None):
            raise ArgumentParseError(
                'Unknown input format "{0}". Valid formats are "bam" and "sam"',
                iformat)
        self.iformat = iformat
        # Decoding the file with the package-wide safe fallback
        # encoding, we avoid having to handle UnicodeDecodeErrors here.
        if ifile == '-':
            self.ifo = sys.stdin.buffer
        else:
            self.ifo = open(ifile, 'rb')

        try:
            self.glimpse = self.ifo.read(256)
            if not self.glimpse:
                raise FormatParseError('Empty input.')
            self.a_bam = is_bam(io.BytesIO(self.glimpse))

            if self.a_bam:
                if iformat == 'sam':
                    raise FormatParseError(
                        'The input looks like BAM format. Expected SAM.'
                        )
                self.line_generator = self.bam_iter()
                self.buf = gzip._PaddedFile(self.ifo, self.glimpse)
            else:
                if iformat == 'bam':
                    raise FormatParseError(
                        'The input is not in BAM format.'
                        )
                self.line_generator = self.sam_iter()
                self.buf = io.BytesIO(self.glimpse)
        except:
            self.close()
            raise

    def bam_iter (self):
        # gzip.open could be used instead of gzip.GzipFile.
        gunzip = gzip.GzipFile(fileobj=self.buf)
        hdr_length = int.from_bytes(gunzip.read(8)[4:8], 'little')
        bytes_yielded = 0
        while bytes_yielded < hdr_length:
            hdr_line = gunzip.readline(hdr_length - bytes_yielded
                                       ).decode(FALLBACKENCODING)
            bytes_yielded += len(hdr_line)
            if bytes_yielded == hdr_length:
                hdr_line.strip('\x00')
            yield hdr_line

    def sam_iter (self):
        bytes_yielded = 0
        while True:
            # refill readahead buffer
            self.buf.seek(0, io.SEEK_END)
            self.buf.write(self.ifo.readline())
            self.buf.seek(bytes_yielded)
            # get next line to yield
            hdr_line = self.buf.readline().decode(FALLBACKENCODING)
            if not hdr_line or hdr_line[0] != '@':
                break
            bytes_yielded += len(hdr_line)
            yield hdr_line
        # Any header lines have been passed on, now we want to make sure what
        # we read from really looks like a SAM file.
        if not hdr_line.strip('\n'):
            if bytes_yielded == 0:
                raise FormatParseError(
                    'The first input line is empty. This is not a SAM/BAM file.'
                    )
            elif self.buf.read(1) or self.ifo.read(1):
                # Should we have reached the end of the input file,
                # then this is a pure SAM header and that's fine.
                # Otherwise this cannot be SAM format because SAM does
                # not allow an empty line between header and body.
                raise FormatParseError(
                    'Found non SAM format content after a valid SAM header.',
                    help='If this is supposed to be a SAM header file without read information, please note that it may not contain more than one empty line after the header.'
                    )
        else:
            # Verify that the next line is a valid SAM body line.
            # In a SAM file each body line must start
            # with QNAME\tFLAG\t, where QNAME is an ASCII
            # string of up to 254 characters, each in the
            # ord range of 33-126, and FLAG is an integer.
            maybe_sam = True
            line_fields = hdr_line.split('\t')
            # Does it have at least 11 tab-separated fields?
            if len(line_fields) < 11:
                maybe_sam = False
            elif len(line_fields[0]) > 254:
                maybe_sam = False
            elif any(not(33 <= ord(c) <= 126)
                     for c in line_fields[0]):
                maybe_sam = False
            elif not line_fields[2] or \
                 any(not(c.isdigit()) for c in line_fields[1]):
                maybe_sam = False
            if not maybe_sam:
                if bytes_yielded == 0:
                    raise FormatParseError(
                        'The input does not look like a SAM{0} file.'
                        .format('' if self.iformat == 'sam' else ' or BAM')
                        )
                else:
                    raise FormatParseError(
                        'Found non SAM format content after a valid SAM header'
                        )

    def __iter__ (self):
        return self

    def __next__ (self):
        try:
            hdrline = next(self.line_generator)
            if hdrline[1:4] == 'CO\t':
                # CO (comment) lines may contain non-ASCII characters.
                # See if we can decode them with the package default encoding.
                try:
                    hdrline = hdrline.encode(FALLBACKENCODING
                                             ).decode(DEFAULTENCODING)
                except UnicodeDecodeError:
                    pass
            return hdrline.strip('\n')
        except:
            self.close()
            raise

    def close (self):
        if self.ifo is not sys.stdin:
            try:
                self.ifo.close()
            except:
                pass


@tmpfiles.allow_cleanup_on_sigterm    
def faidx (ref_genome, ofile=None, verbose=False):
    """Wrapper around samtools faidx."""

    expected_ofn = ref_genome + '.fai'
    if ofile == expected_ofn:
        ofile = None
    if ofile:
        expected_ofn = ofile

    tmp_files = []
    try:
        if ofile:
            if verbose:
                print('generating temporary fasta file for indexing ...')
            tmp_files.append(
                tmpfiles.tmp_hardlink(ref_genome, 'tmp_genome', '.fa')
                )
            ref_genome = tmp_files[-1]

        command = SamtoolsCall(subcommand='faidx',
                               args=[ref_genome],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        if verbose:
            print('running samtools faidx on "{0}" ...'.format(ref_genome))
        if ofile:
            tmp_files.append(ref_genome + '.fai')
        command.run()
        if command.run_info.errors:
            msg = 'Failed to index file "{0}".'.format(ref_genome)
            raise SamtoolsRuntimeError(msg, command.run_info.call,
                                            command.run_info.errors)
        if verbose:
            print('command: "{0}" finished.'.format(command.run_info.call))

        if ofile:
            print('moving index file to final destination ...')
            shutil.move(tmp_files[-1], ofile)
            tmp_files.pop()
    finally:
        for file in tmp_files:
            try:
                os.remove(file)
            except:
                pass
                    
    assert os.path.isfile(expected_ofn), \
           'Something unexpected happened. Could not generate index file.'
    if verbose:
        print('index file is at: "{0}"'.format(expected_ofn))
    return command.run_info


@tmpfiles.allow_cleanup_on_sigterm
def index (inputfile, ofile = None, reindex = False, verbose = False):
    """Wrapper around samtools index."""

    if not is_bam(inputfile):
        raise FormatParseError(
            'Indexing requires an input file in bam format.'
            )
    expected_ofn = inputfile + '.bai'
    if ofile == expected_ofn:
        ofile = None
    if ofile:
        expected_ofn = ofile
    if os.path.exists(expected_ofn) and not reindex:
        if verbose:
            print(
                'Destination file "{0}" exists. No action is required.'
                .format(expected_ofn)
                )
        return SamtoolsReturnValue('', '', '')

    tmp_files = []
    try:
        if ofile:
            if verbose:
                print('generating temporary bam file for indexing ...')
            tmp_files.append(
                tmpfiles.tmp_hardlink(inputfile, 'tmp_bam', '.bam')
                )
            inputfile = tmp_files[-1]

        command = SamtoolsCall(subcommand='index',
                               args=[inputfile],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        if verbose:
            print('running samtools index on "{0}" ...'.format(inputfile))
        if ofile:
            tmp_files.append(inputfile + '.bai')
        command.run()
        if command.run_info.errors:
            msg = 'Failed to index file "{0}".'.format(inputfile)
            raise SamtoolsRuntimeError(msg, command.run_info.call,
                                            command.run_info.errors)
        if verbose:
            print('command: "{0}" finished.'.format(command.run_info.call))

        if ofile:
            if verbose:
                print('moving index file to final destination ...')
            shutil.move(tmp_files[-1], ofile)
            tmp_files.pop()
    finally:
        for file in tmp_files:
            try:
                os.remove(file)
            except:
                pass
            
    assert os.path.isfile(expected_ofn), \
           'Something unexpected happened. Could not generate index file.'
    if verbose:
        print()
        print('index file is at: "{0}"'.format(expected_ofn))
    return command.run_info


def reheader (template, inputfile, outputfile = None, verbose = False):
    """Wrapper around samtools reheader."""

    if isinstance (template, str):        
        call_args = [template, inputfile]
        stdin_pipe = None
        input_data = None
    elif isinstance (template, dict):
        call_args = ['-', inputfile]
        stdin_pipe = subprocess.PIPE
        input_data = str(template)
    if outputfile:
        stdout_pipe = open(outputfile, 'wb')
    else:
        stdout_pipe = None
    if verbose:
        print('generating new bam from {0} with new header from template {1}'
              .format(inputfile, template))

    command = SamtoolsCall(subcommand='reheader',
                           args=call_args,
                           stdout=stdout_pipe,
                           stderr=subprocess.PIPE,
                           stdin=stdin_pipe,
                           input=input_data)
    command.run()
    if outputfile:
        stdout_pipe.close()
    if command.run_info.errors:
        msg = 'Could not reheader input file {0}.'.format(inputfile)
        raise SamtoolsRuntimeError(msg, command.run_info.call,
                                        command.run_info.errors)
    return command.run_info


@tmpfiles.allow_cleanup_on_sigterm   
def sort (ifile, ofile = None, iformat = None, oformat = 'bam',
          maxmem = None, threads = None,
          by_read_name = False, compression_level = None):
    """Wrapper around samtools sort.

    Improvements over wrapped tool:
    - ensures cleanup of temporary files upon unexpected termination of samtools,
      where samtools would leave them behind;
    - never pollutes the final output directory with temporary files;
    - treats errors more consistently than samtools;
    - simpler call signature.
    """

    # Define samtools sort stderr output signatures
    # that indicate an error despite a 0 return code.
    # With samtools 1.x we have not yet found any such signature.
    fatal_strings = []

    # sanitize parameters
    if oformat not in ('sam', 'bam'):
        raise ArgumentParseError(
            'Unknown output format "{0}". Valid formats are "bam" and "sam"',
            oformat)
    if iformat not in ('sam', 'bam', None):
        raise ArgumentParseError(
            'Unknown input format "{0}". Valid formats are "bam" and "sam"',
            iformat)
    # if no input format is specified, we let samtools autodetect it,
    # otherwise we do a fast precheck
    if iformat == 'sam' and is_bam(ifile):
        raise FormatParseError('The input looks like BAM format. Expected SAM.')
    if iformat == 'bam' and not is_bam(ifile):
        raise FormatParseError('The input is not in BAM format.')
    if not threads:
        threads = config.multithreading_level
    # Calculate per-thread memory allowance.
    # The fixed factor 2.5 is required because samtools sticks only losely
    # to the indication and overconsumes memory especially for large input
    # files. The chosen factor prevents overconsumption for files beyond
    # 150 GB (the actual limit is untested), but moderately reduces
    # performance for smaller files.
    maxmem = int((maxmem or config.max_memory)*10**9 / (threads * 2.5))
        
    # construct the call to samtools sort
    tmp_output = tmpfiles.unique_tmpfile_name('MiModD_sort','')
    call = []
    if by_read_name:
        call.append('-n')
    if compression_level:
        call += ['-l', str(compression_level)]
    call += ['-@', str(threads),
             '-m', str(maxmem),
             '-O', oformat,
             '-T', tmp_output]
    if ofile:
        call += ['-o', ofile]
        call_stdout = subprocess.PIPE
    else:
        call_stdout = None
    call.append(ifile)

    # run samtools sort
    cmd = SamtoolsCall(subcommand='sort',
                       args=call,
                       stdout=call_stdout,
                       stderr=subprocess.PIPE)
    try: # we may need to delete temporary files created by samtools
        retcode = cmd.run()
        # check for errors with sort call
        if retcode or any([msg in cmd.run_info.errors
                           for msg in fatal_strings]):
            # can't rely on return code alone here
            # because samtools sort inappropriately returns 0 with
            # some errors
            msg = 'Failed to sort file {0}.'.format(ifile)
            raise SamtoolsRuntimeError(msg, cmd.run_info.call, cmd.run_info.errors)
    except:
        # try to remove temporary files created by samtools
        # that may have been left behind
        for file in glob.iglob(tmp_output + '.*.bam'):
            try:
                os.remove(file)
            except:
                pass
        raise
    return cmd.run_info


def cat (infiles, outfile, oformat, headerfile = None):
    """Wrapper around samtools cat, but with additional header management."""

    if oformat not in ('sam', 'bam'):
        raise ArgumentParseError(
            'Unknown output format "{0}". Valid formats are bam and sam.',
            oformat
            )

    if len(infiles) > 1:
        # preparing a samtools cat call
        call_args = []
        if headerfile:
            call_args += ['-h', headerfile]
        if oformat == 'bam':
            call_args += ['-o', outfile]
        for file in infiles:
            call_args.append(file)
        cat_command = SamtoolsCall(subcommand='cat',
                                   args=call_args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # running the call
        if oformat == 'sam':
            # With sam as the output format, we want to pipe
            # the result of the cat call to samtools view for format
            # conversion. Here we set up this additional call, launch the
            # cat call, connect its stdout to the stdin of our new call and
            # launch this too.
            call_args = ['-h', '-o', outfile, '-']
            cat_command.start()
            view_command = SamtoolsCall(subcommand='view',
                                        args=call_args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdin=cat_command.Popen.stdout)
            view_command.start()
            cat_command.Popen.stdout.close()
            view_command.run(start=False)
            run_info = view_command.run_info
        else:
            # With bam as the output format we can simply launch our prebuilt
            # cat call.
            cat_command.run()
            run_info = cat_command.run_info
        if run_info.errors:
            msg = 'Could not concatenate the input files.'
            raise SamtoolsRuntimeError(msg, run_info.call, run_info.errors)
        return run_info
    else:
        # with only one file just rewrite it using samtools view, but
        # respect output format
        ret = view(infiles[0], 'bam', outfile, oformat)
        return ret

    
def view (infile, iformat, outfile = None, oformat = None, threads = None):
    """Simple wrapper around samtools view."""

    if not iformat in ('sam', 'bam'):
        raise ArgumentParseError(
            'Invalid input format "{0}". Expected "sam" or "bam".',
            iformat)
    if not oformat:
        if iformat == 'sam':
            oformat = 'bam'
        elif iformat == 'bam':
            oformat = 'sam'
    if not oformat in ('sam', 'bam'):
        raise ArgumentParseError(
            'Invalid output format "{0}". Expected "sam" or "bam".',
            oformat)

    if not threads:
        threads = config.multithreading_level
    fatal_strings = []
    call = []
    if oformat == 'bam':
        call.append('-b')
        call.extend(['-@', str(threads)])
    elif oformat == 'sam':
        call.append('-h')
    if iformat == 'sam':
        call.append('-S')
    if outfile:
        call.extend(['-o', outfile])
        call_stdout = subprocess.PIPE
    else:
        call_stdout = None
    call.append(infile)

    cmd = SamtoolsCall(subcommand='view',
                       args=call,
                       stdout=call_stdout,
                       stderr=subprocess.PIPE)
    retcode = cmd.run()
    
    if retcode or any([msg in cmd.run_info.errors for msg in fatal_strings]):
        # see sort() for rationale behind this
        msg = 'Conversion from {0} to {1} failed for file {2}.'.format(
            iformat.upper(), oformat.upper(), infile)
        raise SamtoolsRuntimeError(msg, cmd.run_info.call, cmd.run_info.errors)

    return cmd.run_info
