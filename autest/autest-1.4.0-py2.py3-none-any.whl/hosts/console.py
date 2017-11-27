from __future__ import absolute_import, division, print_function
import sys
import os
import linecache
import colorama

from . import interfaces

# clean this up
reset_stream = "{{host.reset-stream}}"


class ConsoleHost(interfaces.UIHost):
    """description of class"""

    def __init__(self, parser):
        args, unknown = parser.parse_known_args()

        self.__verbose = [] if args.verbose is None else args.verbose
        self.__debug = [] if args.debug is None else args.debug

        if os.name == 'nt':
            colorama.init(wrap=False)
            self.__stdout__ = colorama.AnsiToWin32(sys.__stdout__).stream
            self.__stderr__ = colorama.AnsiToWin32(sys.__stderr__).stream
        else:
            colorama.init()
            self.__stdout__ = sys.__stdout__
            self.__stderr__ = sys.__stderr__

    # our overrides
    def formatStack(self, stack):

        if stack is not None:
            filename, lineno, routine = stack
        else:
            frame = sys._getframe(5)
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            routine = frame.f_code.co_name
        content = self.get_contents(filename, lineno)
        msg = ' File: "{filename}", line: {lineno}, in "{routine}"\n{content}\n'.format(
            filename=filename,
            lineno=lineno,
            routine=routine,
            content=content
            )
        return msg


    def get_contents(self, filename, lineno):
        content = ''
        lineno_color = colorama.Fore.MAGENTA + colorama.Style.NORMAL
        arrow_color = colorama.Fore.LIGHTGREEN_EX
        code_color = colorama.Fore.WHITE + colorama.Style.DIM
        error_code_color = colorama.Fore.LIGHTRED_EX

        if lineno > 3:
            content += " {lineno_color}{lineno}:     {code_color}{line}".format(
                    lineno_color=lineno_color,
                    code_color=code_color,
                    line=linecache.getline(filename, lineno - 3),
                    lineno=lineno - 3
                )
        if lineno > 2:
            content += " {lineno_color}{lineno}:     {code_color}{line}".format(
                lineno_color=lineno_color,
                code_color=code_color,
                line=linecache.getline(filename, lineno - 2),
                lineno=lineno - 2
            )
        if lineno > 1:
            content += " {lineno_color}{lineno}:     {code_color}{line}".format(
                lineno_color=lineno_color,
                code_color=code_color,
                line=linecache.getline(filename, lineno - 1),
                lineno=lineno - 1
            )
        content += " {lineno_color}{lineno}:{arrow_color}==>  {error_code_color}{line}".format(
            lineno_color=lineno_color,
            error_code_color=error_code_color,
            arrow_color=arrow_color,
            lineno=lineno,
            line=linecache.getline(filename, lineno)
        )
        content += " {lineno_color}{lineno}:     {code_color}{line}".format(
            lineno_color=lineno_color,
            code_color=code_color,
            line=linecache.getline(filename, lineno + 1),
            lineno=lineno + 1
        ) + reset_stream
        return content


# class C io streams

    def writeStdOut(self, msg):
        self.__stdout__.write(msg.replace(reset_stream, ""))

    def writeStdErr(self, msg):
        self.__stderr__.write(msg)

# our virtual streams

    def writeMessage(self, msg):
        stream_color = colorama.Style.BRIGHT
        stream_reset = colorama.Style.RESET_ALL + stream_color
        reset = colorama.Style.RESET_ALL
        self.__stdout__.write(stream_color + msg.replace(reset_stream,
                                                         stream_reset) + reset)
        self.__stdout__.flush()

    def writeWarning(self, msg, stack=None, show_stack=True):
        stream_color = colorama.Fore.LIGHTYELLOW_EX
        stream_reset = colorama.Style.RESET_ALL + stream_color
        reset = colorama.Style.RESET_ALL
        self.__stdout__.write(stream_color + msg.replace(reset_stream,
                                                         stream_reset) + reset)
        self.__stdout__.flush()

    def writeError(self, msg, stack=None, show_stack=True, exit=True):
        stream_color = colorama.Fore.LIGHTRED_EX
        stream_reset = colorama.Style.RESET_ALL + stream_color
        reset = colorama.Style.RESET_ALL
        self.__stderr__.write(stream_color + msg.replace(reset_stream,
                                                         stream_reset) + reset)
        self.__stderr__.flush()

    def writeDebug(self, catagory, msg):
        '''
        prints a debug message
        catagorty - is the type of verbose message
        msg - is the message to print
        The host may or may not be given all trace messages
        by the engine. The catagory is not added to the message.
        The host can use this value help orginize messages, it is suggested
        that a given message is clearly formatted with the catagory type.
        '''
        stream_color = colorama.Fore.GREEN
        stream_reset = colorama.Style.RESET_ALL + stream_color
        reset = colorama.Style.RESET_ALL
        self.__stdout__.write(stream_color + msg.replace(reset_stream,
                                                         stream_reset) + reset)
        self.__stdout__.flush()

    def writeVerbose(self, catagory, msg):
        '''
        prints a verbose message
        catagorty - is the type of verbose message
        msg - is the message to print
        The host may or may not be given all verbose messages
        by the engine. The catagory is not added to the message.
        The host can use this value help orginize messages, it is suggested
        that a given message is clearly formatted with the catagory type.
        '''
        stream_color = colorama.Fore.CYAN
        stream_reset = colorama.Style.RESET_ALL + stream_color
        reset = colorama.Style.RESET_ALL
        self.__stdout__.write(stream_color + msg.replace(reset_stream,
                                                         stream_reset) + reset)
        self.__stdout__.flush()

    def writeProgress(self, task, msg=None, progress=None, completed=False):
        '''
        task - string telling the current activity we are doing
        status - string telling the current state of the task
        progress - is a value between 0 and 1, -1 means unknown
        completed - tell us to stop displaying the progress

        Will(/might) extend latter with:
        id - an ID that distinguishes each progress bar from the others.
        parentid - tell the parent task to this progress. ( allow formatting improvments to show relationships)
        time_left - a value to tell us an ETA in some time value

        '''
        pass

    @property
    def debugCatagories(self):
        '''
        returns list of string defining the catagories of debug messages we want to have
        processed by the engine
        '''
        return self.__debug

    @property
    def verboseCatagories(self):
        '''
        returns list of string defining the catagories of verbose messages we want to have
        processed by the engine
        '''
        return self.__verbose
