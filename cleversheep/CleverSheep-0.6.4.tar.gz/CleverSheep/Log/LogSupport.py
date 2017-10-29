#!/usr/bin/env python
"""Various utilities that are useful in logging.

"""

import sys

from CleverSheep.Prog import Files


def openFullPublicLog(path, mode="w"):
    """Open log file that is totally public.

    """
    f = open(path, mode)
    Files.chmod(path, "a+rw")
    return f


class HangStream(object):
    r"""Wraps an output stream to provide hanging prefixes.

    You can use this to wrap a file like object. Blocks of text are reformatted
    to have a hanging prefix, such as a time stamp. For example::

        10:30:22 Started
        10:30:24 This is a long,
                 multi-line
                 message
        10:30:59 Finished.

    You can use this like a normal stream. It tracks new lines so the following
    code will produce output like the above example:<py>:

    |    hs.write("Start")
    |    hs.write("ed\\n")
    |    hs.write("This is a long,\\nmulti-line\\nmessage\\n")
    |    hs.write("Finished\\n")

    """

    def __init__(self, f=sys.stdout, getPrefix=lambda: ""):
        """Initialise a HangStream Instance.

        :param f: A file like object, it is expected to have a 'flush' and
                 'write' method.
        :param getPrefix: A function that when called returns a string prefix
                         which will be appended to the written lines.

        A common example of the prefix function would be one that returns
        the current time.
        """
        self.f = f
        self._newLine = True
        self._getPrefix = getPrefix
        self._prefix = self._getPrefix()

    def write(self, s):
        """Write out a line. Note that and new lines within the string will
        not be removed.

        :param s: The string to write out
        :return: None
        """
        return self.writelines(s.splitlines(True))

    def writelines(self, lines):
        r"""Write out the passed in lines. If a line does not end with a '\n'
        it is assumed the next line is part of the same output and the prefix
        will not be applied.

        :param lines: A list of lines to be written out
        :return: None
        """
        if not lines:
            return

        prefix = ""
        if self._newLine:
            self._prefix = prefix = self._getPrefix()
        for line in lines:
            self.f.write("%s%s" % (prefix, line))
            prefix = " " * len(self._prefix)

        if lines[-1][-1] == "\n":
            self._newLine = True
        else:
            self._newLine = False

    def flush(self):
        """Flush self.f"""
        if self.f:
            self.f.flush()
