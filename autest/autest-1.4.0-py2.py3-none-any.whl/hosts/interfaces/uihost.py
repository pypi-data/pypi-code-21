from __future__ import absolute_import, division, print_function
import abc


class UIHost(object):
    """description of class"""

    # class C io streams
    @abc.abstractmethod
    def writeStdOut(self, msg):
        raise NotImplementedError

    @abc.abstractmethod
    def writeStdErr(self, msg):
        raise NotImplementedError

# our virtual streams

    @abc.abstractmethod
    def writeMessage(self, msg):
        raise NotImplementedError

    @abc.abstractmethod
    def writeWarning(self, msg, stack=None, show_stack=False):
        raise NotImplementedError

    @abc.abstractmethod
    def writeError(self, msg, stack=None, show_stack=True,exit=True):
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractproperty
    def debugCatagories(self):
        return []

    @abc.abstractproperty
    def verboseCatagories(self):
        return []

    # Format our virtual streams
    # these are not required but allow custom formating
    # from the default formatting which can be useful
    # for output hosts that write to certain file formats

    def formatMessage(self, msg_list, sep=' ', end='\n', **kw):
        return None

    def formatWarning(self,
                      msg_list,
                      sep=' ',
                      end='\n',
                      stack=None,
                      show_stack=False,
                      **kw):
        return None

    def formatError(self,
                    msg_list,
                    sep=' ',
                    end='\n',
                    stack=None,
                    show_stack=True,
                    **kw):
        return None

    def formatDebug(self, catagory, msg_list, sep=' ', end='\n', **kw):
        return None

    def formatVerbose(self, catagory, msg_list, sep=' ', end='\n', **kw):
        return None

    def formatProgress(self, task, msg=None, progress=None, completed=False):
        return None

    def formatStack(self, stack):
        return None
