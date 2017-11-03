from __future__ import absolute_import, division, print_function
import sys
import linecache

from .interfaces import uihost
from .common import is_a

# this class does two functions
# 1) formats the message
# 2) dispatch the message to all output hosts


class Formatter(uihost.UIHost):
    def __init__(self, defaultHost):
        self.__default_host = defaultHost
        self.__hosts = [self.__default_host]

        self.__verbose = []
        self.__debug = []
        self.__host_verbose_catagory = defaultHost.verboseCatagories
        self.__host_debug_catagory = defaultHost.debugCatagories

    def AddHost(self, host):
        #<fill in>
        self.__host_verbose_catagory = host.verboseCatagories
        self.__host_debug_catagory = host.debugCatagories

    def ShutDown(self):
        pass

    def MapStream(self, msg, orig_stream):
        pass

    def get_contents(self, filename, lineno):
        content = ''
        if lineno > 3:
            content += "   {0}".format(linecache.getline(filename, lineno - 3))
        if lineno > 2:
            content += "    {0}".format(
                linecache.getline(filename, lineno - 2))
        if lineno > 1:
            content += "    {0}".format(
                linecache.getline(filename, lineno - 1))
        content += "->  {0}".format(linecache.getline(filename, lineno))
        content += "    {0}".format(linecache.getline(filename, lineno + 1))
        return content

    # Functions to find matching catagory of message
    # for different cases

    # Get the global value setup by --verbose
    def _get_verbose_catagory(self, catagory):
        for c in catagory:
            if c.lower() in self.__verbose:
                return catagory[0]

# Get the global value setup by --debug

    def _get_debug_catagory(self, catagory):
        for c in catagory:
            if c.lower() in self.__verbose:
                return catagory[0]

    # Get if any of the output host have special catagories
    # to be processed
    # This is for Verbose. Not test if any host has on, not which
    def _get_host_verbose_catagory(self, catagory):
        for c in catagory:
            if c.lower() in self.__host_verbose_catagory:
                return c, catagory[0]
        return None, None

    # This is for debug. Not test if any host has on, not which
    def _get_host_debug_catagory(self, catagory):
        for c in catagory:
            if c.lower() in self.__host_debug_catagory:
                return c, catagory[0]
        return None, None

    # for the stack information
    def formatStack(self, host, stack):
        # Does Host want to do the formatting
        msg = host.formatStack(stack)
        # If this is None, we will do the formating
        if not msg:
            if stack is not None:
                filename, lineno, routine = stack
            else:
                frame = sys._getframe(4)
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                routine = frame.f_code.co_name
            content = self.get_contents(filename, lineno)
            msg = ' File: "%s", line: %s, in "%s"\n %s\n' % (filename, lineno,
                                                             routine, content)
        return msg

    def _formatStdOut(self, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        return msg

    def _formatStdErr(self, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        return msg

    def _formatMessage(self, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        return msg

    def _formatWarning(self, host, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        if kw.get('show_stack', False):
            stack = kw.get('stack')
            msg += self.formatStack(host, stack)
        msg = "Warning: {0}".format(msg)
        return msg

    def _formatError(self, host, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        if kw.get('show_stack', True):
            stack = kw.get('stack')
            msg += self.formatStack(host, stack)
        msg = "Error: {0}".format(msg)
        return msg

    def _formatVerbose(self, catagory, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        msg = "Verbose: [{0}] {1}".format(catagory, msg)
        return msg

    def _formatDebug(self, catagory, msglst, **kw):
        msg = kw.get('sep', ' ').join(msglst) + kw.get('end', '\n')
        msg = "Debug: [{0}] {1}".format(catagory, msg)
        return msg

    def writeStdOut(self, msg_list, **kw):
        fmsg = None
        if not is_a.List(msg_list):
            msg_list = [str(msg_list)]
        for h in self.__hosts:
            msg = h.FormatStdOut(msg_list, **kw)
            if not msg and not fmsg:
                fmsg = self._formatStdOut(msg_list, **kw)
            if not msg:
                msg = fmsg

            h.writeStdOut(msg)

    def writeStdErr(self, msg_list, **kw):
        fmsg = None
        if not is_a.List(msg_list):
            msg_list = [str(msg_list)]
        for h in self.__hosts:
            msg = h.FormatStdErr(msg_list, **kw)
            if not msg and not fmsg:
                fmsg = self._formatStdErr(msg_list, **kw)
            if not msg:
                msg = fmsg
            h.writeStdErr(msg)

    def writeMessage(self, msg_list, **kw):
        fmsg = None
        if not is_a.List(msg_list):
            msg_list = [str(msg_list)]
        for h in self.__hosts:
            msg = h.formatMessage(msg_list, **kw)
            if not msg and not fmsg:
                fmsg = self._formatMessage(msg_list, **kw)
            if not msg:
                msg = fmsg
            h.writeMessage(msg)

    def writeWarning(self, msg_list, **kw):
        fmsg = None
        if not is_a.List(msg_list):
            msg_list = [str(msg_list)]
        for h in self.__hosts:
            msg = h.formatWarning(msg_list, **kw)
            if not msg and not fmsg:
                fmsg = self._formatWarning(h, msg_list, **kw)
            if not msg:
                msg = fmsg
            h.writeWarning(msg, **kw)

    def writeError(self, msg_list, **kw):
        fmsg = None
        if not is_a.List(msg_list):
            msg_list = [str(msg_list)]
        for h in self.__hosts:
            msg = h.formatError(msg_list, **kw)
            if not msg and not fmsg:
                fmsg = self._formatError(h, msg_list, **kw)
            if not msg:
                msg = fmsg
            h.writeError(msg, **kw)

        if kw.get("exit", True):
            sys.exit(msg)

    def writeDebug(self, catagory, msg_list, **kw):
        fmsg = None
        cat = self._get_debug_catagory(catagory)
        if cat is None:
            # see if we have a host that needs certain catagory
            match, cat = self._get_host_debug_catagory(catagory)
            if cat:  # we have something
                # go through the hosts as see if out match is in the
                # set of items for a given Host
                for h in self.__hosts:
                    # does this host care
                    if h.debugCatagories and match in h.debugCatagories:
                        # it does so we make the message
                        if not is_a.List(msg_list):
                            msg_list = [str(msg_list)]
                        msg = h.formatDebug(cat, msg_list, **kw)
                        if not msg and not fmsg:
                            fmsg = self._formatDebug(cat, msg_list, **kw)
                        if not msg:
                            msg = fmsg
                        h.writeDebug(cat, msg)
            return
        else:
            for h in self.__hosts:
                msg = h.formatDebug(cat, msg_list, **kw)
                if not msg and not fmsg:
                    fmsg = self._formatDebug(cat, msg_list, **kw)
                if not msg:
                    msg = fmsg
                h.writeDebug(cat, msg)

    def writeVerbose(self, catagory, msg_list, **kw):
        fmsg = None
        cat = self._get_verbose_catagory(catagory)
        if cat is None:
            # see if we have a host that needs certain catagory
            match, cat = self._get_host_verbose_catagory(catagory)
            if cat:  # we have something
                # go through the hosts as see if out match is in the
                # set of items for a given Host
                for h in self.__hosts:
                    # does this host care
                    if h.verboseCatagories and match in h.verboseCatagories:
                        # it does so we make the message
                        if not is_a.List(msg_list):
                            msg_list = [str(msg_list)]
                        msg = h.formatVerbose(cat, msg_list, **kw)
                        if not msg and not fmsg:
                            fmsg = self._formatVerbose(cat, msg_list, **kw)
                        if not msg:
                            msg = fmsg
                        h.writeVerbose(cat, msg)
            return
        else:
            for h in self.__hosts:
                msg = h.formatVerbose(cat, msg_list, **kw)
                if not msg and not fmsg:
                    fmsg = self._formatVerbose(cat, msg_list, **kw)
                if not msg:
                    msg = fmsg
                h.writeVerbose(cat, msg)

    def writeProgress(self,
                      task,
                      msg_list=None,
                      progress=None,
                      completed=False):
        for h in self.__hosts:
            h.writeProgress(catagory, task, msg_list, progress, completed)
