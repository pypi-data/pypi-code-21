from __future__ import absolute_import, division, print_function

import hosts.output as host

import threading
import re
import os
import sys
import traceback


class PipeRedirector(object):
    '''
    This class redirects and output stream to stream handler that can then process the data on
    the different streams provided by the uihost. In the case of the command that this is used
    for this primarly lets us sort the data into different stream files for testing purposes
    '''

    def _readerthread(self):

        line = ' '
        try:
            while line:
                line = self.pipein.readline()
                if line:
                    self.writer(line)
                    host.WriteDebug(['process_output'], line.decode(), end='')
        except:
            # There was an error... that shouldn't happen, but still it did. So we report it
            # to the caller and close our pipe end so that spawned program
            # won't block
            self.error = traceback.format_exc()
            self.pipein.close()
            self.pipein = None

        # for i in iter(self.pipein):
#            i=i.decode("utf-8")
#            self.writer(i)
#            host.WriteDebug(['process_output'],i,end='')

    def __init__(self, pipein, writer):
        self.pipein = pipein
        self.writer = writer
        self.thread = threading.Thread(
            target=self._readerthread,
            args=()
        )
        self.executing = True
        self.thread.start()

    def close(self):
        if self.executing == True:
            self.executing = False
            self.thread.join()
            self.pipein = None
            self.thread = None
            self.writer = None

test_search = 0
test_match = 1

verbose_tests = [
    (test_match, re.compile('^verbose: ', re.IGNORECASE))
]

debug_tests = [
    (test_match, re.compile('^debug: ', re.IGNORECASE)),
    (test_match, re.compile('^trace: ', re.IGNORECASE)),
]

warning_tests = [
    (test_search, re.compile(
        '(\A|\s)warning?\s?(([?!: ])|(\.\s))\D', re.IGNORECASE))
]

error_tests = [
    (test_search, re.compile(
        '(\A|\s)error?\s?(([?!: ])|(\.\s))\D', re.IGNORECASE)),
    (test_match, re.compile('fail$', re.IGNORECASE))
]


def do_test(test, str):
    if test[0] == test_search:
        return test[1].search(str)
    elif test[0] == test_match:
        return test[1].match(str)


def is_error(str):
    for test in error_tests:
        if do_test(test, str):
            return True
    return False


def is_warning(str):
    for test in warning_tests:
        if do_test(test, str):
            return True
    return False


def is_verbose(str):
    for test in verbose_tests:
        if do_test(test, str):
            return True
    return False


def is_debug(str):
    for test in debug_tests:
        if do_test(test, str):
            return True
    return False

full_stream_file = 'stream.all.txt'
out_stream_file = 'stream.stdout.txt'
err_stream_file = 'stream.stderr.txt'
# message_stream_file='stream.message.txt'
error_stream_file = 'stream.error.txt'
warning_stream_file = 'stream.warning.txt'
verbose_stream_file = 'stream.verbose.txt'
debug_stream_file = 'stream.debug.txt'


class StreamWriter(object):

    stdout = 0
    stderr = 1

    def __init__(self, path, cmd, env):
        self.__lock = threading.Lock()

        if os.path.exists(path) == False:
            os.makedirs(path)

        self.FullFile = os.path.join(path, full_stream_file)
        self.StdOutFile = os.path.join(path, out_stream_file)
        self.StdErrFile = os.path.join(path, err_stream_file)
        # self.MessageFile=os.path.join(path,message_stream_file)
        self.ErrorFile = os.path.join(path, error_stream_file)
        self.WarningFile = os.path.join(path, warning_stream_file)
        self.VerboseFile = os.path.join(path, verbose_stream_file)
        self.DebugFile = os.path.join(path, debug_stream_file)

        cmdfile = open(os.path.join(path, "command.txt"), 'wb')
        cmdfile.write("Command= {0}\n".format(cmd).encode("utf-8"))
        cmdfile.close()

        with open(os.path.join(path, "replay.sh"), 'wb') as f:
            f.write(self.gen_bash_script(cmd, env).encode("utf-8"))

        self.both = open(self.FullFile, 'wb')
        self.outfile = open(self.StdOutFile, 'wb')
        self.errfile = open(self.StdErrFile, 'wb')

        self.warningfile = open(self.WarningFile, 'wb')
        self.errorfile = open(self.ErrorFile, 'wb')
        self.verbosefile = open(self.VerboseFile, 'wb')
        self.debugfile = open(self.DebugFile, 'wb')

        self.cache = []

    def gen_powershell_script(self):
        pass

    def gen_fish_script(self):
        pass

    def gen_bash_script(self, cmd, env):
        ret = "#!/bin/bash\n"
        ret += self.gen_set_env(env, "export {0}=\"{1}\"\n")
        ret += cmd + "\n"
        return ret

    def gen_set_env(self, env, set_str):
        ret = "\n"
        for k, v in env.items():
            ret += set_str.format(k, v)
        return ret

    def _smart_match(self, str):
        if is_error(str):
            self.errorfile.write(str.encode("utf-8"))
            return True
        elif is_warning(str):
            self.warningfile.write(str.encode("utf-8"))
            return True
        elif is_verbose(str):
            self.verbosefile.write(str.encode("utf-8"))
            return True
        elif is_debug(str):
            self.debugfile.write(str.encode("utf-8"))
            return True
        return False

    def WriteStdOut(self, s):
        '''
        store the data in the cache of all outputted data
        '''
        s = s.decode()
        with self.__lock:
            if self.cache == []:
                # cache is empty
                self.cache.append([StreamWriter.stdout, s])
            elif self.cache[-1][0] == StreamWriter.stdout:
                # if last item in cache is the same as the current item, we add
                # the data
                self.cache[-1][1] += s
            else:
                # there is data but it is of a different type
                self.cache.append([StreamWriter.stdout, s])

    def WriteStdErr(self, s):
        s = s.decode()
        with self.__lock:
            if self.cache == []:
                # cache is empty
                self.cache.append([StreamWriter.stderr, s])
            elif self.cache[-1][0] == StreamWriter.stderr:
                # if last item in cache is the same as the current item, we add
                # the data
                self.cache[-1][1] += s
            else:
                # there is data but it is of a different type
                self.cache.append([StreamWriter.stderr, s])

    def Close(self):
        # write out files
        self._empty_cache()
        # close file handles
        self.both.close()
        self.outfile.close()
        self.errfile.close()

        self.warningfile.close()
        self.errorfile.close()
        self.verbosefile.close()
        self.debugfile.close()

    def _empty_cache(self):

        for text in self.cache:

            if text[0] == StreamWriter.stdout:
                brkup = text[1].split('\n')
                grpstr = ''
                # strip the end if it is ''
                if brkup[-1] == '':
                    brkup = brkup[:-1]
                for s in brkup:
                    if s == '':
                        grpstr += s + '\n'
                    elif grpstr == '':
                        grpstr = s + '\n'
                    elif s[0] == ' ' or s[0] == '\t':  # group indented text
                        grpstr += s + '\n'
                    else:
                        self.both.write(grpstr.encode("utf-8"))
                        if not self._smart_match(grpstr):
                            pass
                        self.outfile.write(grpstr.encode("utf-8"))
                        grpstr = s + '\n'
                else:
                    self.both.write(grpstr.encode("utf-8"))
                    if not self._smart_match(grpstr):
                        pass
                    self.outfile.write(grpstr.encode("utf8"))
            elif text[0] == StreamWriter.stderr:
                brkup = text[1].split('\n')
                grpstr = ''
                # strip the end if it is ''
                if brkup[-1] == '':
                    brkup = brkup[:-1]
                for s in brkup:
                    if s == '':
                        grpstr += s + '\n'
                    elif grpstr == '':
                        grpstr = s + '\n'
                    elif s[0] == ' ' or s[0] == '\t':  # group indented text
                        grpstr += s + '\n'
                    else:
                        self.both.write(grpstr.encode("utf8"))
                        if not self._smart_match(grpstr):
                            pass
                        self.errfile.write(grpstr.encode("utf8"))
                        grpstr = s + '\n'
                else:
                    self.both.write(grpstr.encode("utf8"))
                    if not self._smart_match(grpstr):
                        pass
                    self.errfile.write(grpstr.encode("utf8"))
            else:
                # we have some error or unknown code
                pass
