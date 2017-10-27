import  os
import  datetime
import  threading
import  inspect
import  logging
import  socket
import  pudb

# pfmisc local dependencies
try:
    from    .message        import Message
    from    ._colors        import  Colors
except:
    from    message         import Message
    from    _colors         import  Colors

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s')

class debug(object):
    """
        A simple class that provides some helper debug functions. Mostly
        printing function/thread names and checking verbosity level
        before printing.
    """

    def log(self, *args):
        """
        get/set the log object.

        Caller can further manipulate the log object with object-specific
        calls.
        """
        if len(args):
            self._log = args[0]
        else:
            return self._log

    def name(self, *args):
        """
        get/set the descriptive name text of this object.
        """
        if len(args):
            self.__name = args[0]
        else:
            return self.__name

    def __init__(self, **kwargs):
        """
        Constructor
        """

        self.verbosity              = 0
        self.level                  = 0

        self.b_colorize             = True
        self.b_useDebug             = False
        self.str_debugDirFile       = '/tmp'
        self.__name__               = 'debug'
        for k, v in kwargs.items():
            if k == 'verbosity':    self.verbosity          = v
            if k == 'level':        self.level              = v
            if k == 'debugToFile':  self.b_useDebug         = v
            if k == 'debugFile':    self.str_debugDirFile   = v
            if k == 'within':       self.__name__           = v
            if k == 'colorize':     self.b_colorize         = v

        if self.b_useDebug:
            str_debugDir                = os.path.dirname(self.str_debugDirFile)
            str_debugName               = os.path.basename(self.str_debugDirFile)
            if not os.path.exists(str_debugDir):
                os.makedirs(str_debugDir)
            self.str_debugFile          = '%s/%s' % (str_debugDir, str_debugName)
            self.debug                  = Message(logTo = self.str_debugFile)
            self.debug._b_syslog        = False
            self.debug._b_flushNewLine  = True

        self._log                   = Message()
        self._log._b_syslog         = True
        self.__name                 = "pfmisc"
        self.str_hostname           = socket.gethostname()


    def __call__(self, *args, **kwargs):
        self.qprint(*args, **kwargs)

    def qprint(self, msg, **kwargs):

        str_comms   = "normal"
        self.level  = 0
        self.msg    = ""

        for k, v in kwargs.items():
            if k == 'level':    self.level  = v
            if k == 'msg':      self.msg    = v
            if k == 'comms':    str_comms   = v

        if msg != None:    
            self.msg = msg

        if self.b_useDebug:
            write   = self.debug
        else:
            write   = print

        stack = inspect.stack()
        str_callerFile      = os.path.split(stack[1][1])[1]
        str_callerMethod    = inspect.stack()[1][3]

        if self.level <= self.verbosity:
            if self.b_colorize: write(Colors.CYAN,                                  end="")
            write('%s' % datetime.datetime.now().replace(microsecond=0) + "  | ",   end="")
            if self.b_colorize: write(Colors.LIGHT_CYAN,                            end="")
            write('%15s | ' % self.str_hostname,                                    end="")
            if self.b_colorize: write(Colors.LIGHT_BLUE,                            end="")
            write('%35s' % (str_callerFile + ':' +  
                            self.__name__ + "." + str_callerMethod + '()') + ' | ', end="")
            if self.b_colorize:
                if str_comms == 'normal':   write(Colors.WHITE,                     end="")
                if str_comms == 'status':   write(Colors.PURPLE,                    end="")
                if str_comms == 'error':    write(Colors.RED,                       end="")
                if str_comms == "tx":       write(Colors.YELLOW,                    end="")
                if str_comms == "rx":       write(Colors.GREEN,                     end="")
            if str_comms == "tx":           write("\n---->")
            if str_comms == "rx":           write("\n<----")

            write(msg)

            if not self.b_colorize:
                if str_comms == "tx":       write(Colors.YELLOW,                    end="")
                if str_comms == "rx":       write(Colors.GREEN,                     end="")
                
            if str_comms == "tx":           write("---->")
            if str_comms == "rx":           write("<----")

            if self.b_colorize:         write(Colors.NO_COLOUR, end="")

