# The MIT License (MIT)
#
# Copyright (c) 2016-2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import atexit
import os
import sys
import logging
try:
    import readline
except ImportError:
    readline = False
from botocore.vendored.requests.packages.urllib3 import disable_warnings

import hs3
from hs3.cmd import HS3shell


def main():
    opts = hs3.parseargs()
    if opts.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if readline:
        histfile = os.path.join(os.path.expanduser("~"), ".hs3sh_history")
        # noinspection PyBroadException
        try:
            readline.read_history_file(histfile)
            # default history len is -1 (infinite), which may grow unruly
            readline.set_history_length(1000)
        except Exception:
            # if this goes wrong, silently ignore it...
            pass
        else:
            atexit.register(readline.write_history_file, histfile)

    # disable warning regarding SSL certs that can't be checked
    disable_warnings()
    HS3shell(completekey='Tab').cmdloop()

if __name__ == '__main__':
    main()
