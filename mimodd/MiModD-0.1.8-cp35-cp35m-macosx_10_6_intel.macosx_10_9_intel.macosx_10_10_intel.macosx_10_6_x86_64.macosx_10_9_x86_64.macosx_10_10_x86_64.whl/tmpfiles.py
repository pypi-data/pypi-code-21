import os
import shutil
import random
import signal
import tempfile

from functools import wraps, partial

from . import config
from . import ArgumentParseError, ArgumentValidationError


def _sigterm_handler (signum, frame):
    raise SystemExit('Execution stopped by system.')


def allow_cleanup_on_sigterm (f):
    """Define package-wide behavior on SIGTERM."""

    @wraps(f)
    def catch_sigterm_wrapper (*args, **kwargs):
        try:
            old_sigterm_handler = signal.signal(signal.SIGTERM, _sigterm_handler)
        except ValueError:
            old_sigterm_handler = None
        ret = f(*args, **kwargs)
        if old_sigterm_handler:
            signal.signal(signal.SIGTERM, old_sigterm_handler)
        return ret
    return catch_sigterm_wrapper


NamedTemporaryMiModDFile = partial(
    tempfile.NamedTemporaryFile, dir=config.tmpfile_dir
    )
NamedTemporaryMiModDFile.__doc__ = """\
Create and return a temporary file in the package-wide tmpfile_dir.

The file is created as a NamedTemporaryFile in config.tmpfile_dir.
"""

def remove_temporary_file (file):
    try:
        os.remove(file)
    except:
        pass

    
def tmp_hardlink (ifile, prefix = '', suffix = '', fallback = 'symbolic'):
    """Generate a temporary hard link to an input file.

    Uses unique_tmpfile_name to obtain a randomized name for the link.
    If a hard link cannot be generated because ifile and hard_link point
    to different physical storage devices, a symbolic link or a copy is
    generated instead depending on the fallback argument."""
    
    supported_fallbacks = ('symbolic', 'copy')
    if fallback not in supported_fallbacks:
        msg = 'Unsupported fallback behavior: "{0}". Fallback must be one of: ' \
              + ', '.join(supported_fallbacks) + '.'
        raise ArgumentParseError (msg, fallback)
    hard_link = unique_tmpfile_name(prefix, suffix)
    conditional_hardlink(ifile, hard_link, fallback)
    return hard_link


def conditional_hardlink (ifile, hard_link, fallback = 'symbolic'):
    ifile = os.path.abspath(ifile) # an abspath is required just in case we need to soft-link
    if not os.path.exists(ifile):
        raise ArgumentValidationError('Non-existent input file: {0}.', ifile)
    try:
        try:
            os.link(ifile, hard_link)
            return hard_link
        except OSError as e:
            if e.errno != 18: # catch only Invalid cross-device link
                raise
            if fallback == 'symbolic':
                try:
                    os.symlink(ifile, hard_link)
                except (OSError, NotImplementedError):
                    # user-rights or platform-support missing to create symlink
                    # silently fall back to copying the file
                    pass
                else:
                    if os.path.exists(hard_link) and \
                       os.path.islink(hard_link):
                        return hard_link
            shutil.copyfile(ifile, hard_link)
    except:
        # unsurmountable error
        # try to remove whatever may have been created as hard_link
        # then reraise the error for a diagnosis of the problem
        try:
            # unsafe in the (very) exceptional situation of a race condition
            # involving the random file name returned from unique_tmpfile_name
            os.remove(hard_link)
        except:
            pass
        raise # could use raise from None in Python 3.3+ 


def unique_tmpfile_name (prefix='', suffix=''):
    """Generate a random temporary file name with fixed prefix and suffix.

    Adds a random number between 1 and 10000 between prefix and suffix and
    prepends the name with the temporary file path set in MiModD.config."""
    
    for invalid_char in ('/', '\x00'):
        if invalid_char in prefix:
            raise ArgumentValidationError(
                'Invalid character "{0}" in prefix.'.format(invalid_char),
                prefix)
        if invalid_char in suffix:
            raise ArgumentValidationError(
                'Invalid character "{0}" in suffix.'.format(invalid_char),
                suffix)
    tmp_output_prefix = os.path.join(config.tmpfile_dir, prefix)
    name_template = tmp_output_prefix + '{0}' + suffix
    while True:
        tmp_name = name_template.format(random.randint(1,10000))
        if not os.path.exists(tmp_name):
            return tmp_name
