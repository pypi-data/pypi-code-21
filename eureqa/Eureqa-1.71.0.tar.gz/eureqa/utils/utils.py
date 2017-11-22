 # Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import glob, os
import time
import urllib
from functools import wraps
import warnings

def remove_files_in_directory(dir_path):
    """Removes all files in the specified directory.

    :param str dir_path: Path to files to be removed.
    """
    filelist = glob.glob(os.path.join(dir_path, '*'))
    for f in filelist:
        try:
            os.remove(f)
        except Exception as e:
            print 'Warning: remove_files_in_directory received exception "%s"' % e

def quote(url):
    """ URL-encode 'url'.  Handle non-string values by casting to a string. """
    return urllib.quote(str(url))

def quote_plus(url):
    """ URL-encode 'url' for form submission.  Handle non-string values by casting to a string. """
    return urllib.quote_plus(str(url))

def quote_everything(value):
    """ URL-encode provided value. Does not treat '/' as a safe character and also encodes it."""
    return urllib.quote(str(value), safe='')

class Throttle(object):
    """Decorator that ensures the wrapped function is not called twice within one seconds.
    sleeps for a second if it is called within 1 second of the last call
    must wrap a function that takes at least one argument"""
    def __init__(self):
        # keys are __str__ representation of first argument, values
        # are last call time b/c there is once Throttle object
        # instance for each decorated function (not for each object
        # instance with a decorated function)
        self._last_call_time = {}

    def __call__(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            this_call_time = time.time()
            # pick string representation of the first arg (aka self)
            key = id(args[0])
            # delay the call by a second if it has been less than
            if key in self._last_call_time and this_call_time - self._last_call_time[key] < 1:
                time.sleep(1)

            # Important to set last call to the time this method was called. Not after the sleep.
            # Otherwise it will get into the infinite loop.
            self._last_call_time[key] = this_call_time

            # do the actual work
            return wrapped(*args, **kwargs)

        return wrapper

def _deprecated(msg):
    # This function is mostly a test hook, to make sure that
    # DeprecationWarnings emitted from within the
    # Eureqa module are printed to stderr.
    warnings.warn(msg, DeprecationWarning)
