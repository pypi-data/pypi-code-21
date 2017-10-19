import sys
from os import environ as env

try:
    from termcolor import colored as termcolor_colored #@UnresolvedImport
except:
    sys.stderr.write('procgraph can make use of the package "termcolor". '
                     'Please install it.\n')

    def termcolor_colored(x,
                    color=None, on_color=None, attrs=None): #@UnusedVariable
        ''' emulation of the termcolor interface '''
        return x


def colored(x, color=None, on_color=None, attrs=None):
    colorize = True
    # TODO: no colorize during tests
    if colorize: #@UndefinedVariable
        return termcolor_colored(x, color, on_color, attrs)
    else:
        return x


try:
    from setproctitle import setproctitle #@UnresolvedImport @UnusedImport
except:
    sys.stderr.write('procgraph can make use of the package "setproctitle". '
                     'Please install it.\n')

    def setproctitle(x):
        ''' emulation of the setproctitle interface '''
        pass

screen_columns = None


def get_screen_columns():
    module = sys.modules[__name__]
    if  module.screen_columns is None:
        max_x, max_y = getTerminalSize() #@UnusedVariable
        module.screen_columns = max_x

    return module.screen_columns


def getTerminalSize():
    '''
    max_x, max_y = getTerminalSize()
    '''
    import os

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])


# These should be kwargs to 
#    colored(s, color=None, on_color=None, attrs=None
color_warning = dict(color='yellow')
color_error = dict(color='red')
color_user_error = dict(color='red')
color_info = dict(color='green')
color_debug = dict(color='magenta')


# TODO: use logging
if False:
        
    def warning(string):
        write_message(string, lambda x: 'pg: ' + colored(x, **color_warning))
    
    
    def error(string):
        write_message(string, lambda x: 'pg: ' + colored(x, **color_error))
    
    
    def user_error(string):
        write_message(string, lambda x: 'pg: ' + colored(x, **color_user_error))
    
    
    def info(string):
        write_message(string, lambda x: 'pg: ' + colored(x, **color_info))
    
    
    def debug(string):
        write_message(string, lambda x: 'pg: ' + colored(x, **color_debug))
        
        
    
    def write_message(string, formatting):
        
        sys.stdout.flush()
        string = str(string)
    
        #clean_console_line(sys.stderr)
        lines = string.split('\n')
        if len(lines) == 1:
            sys.stderr.write(formatting(lines[0]) + '\n')
        else:
            for i, l in enumerate(lines): #@UnusedVariable
                #if i == 1: 
                #    l = '- ' + l
                #else:
                #    l = '  ' + l
                sys.stderr.write(formatting(l) + '\n')
    
        sys.stderr.flush()

else:
    
    prefix = ''
    from procgraph import logger
    def warning(string):
        fmt = lambda x: prefix + colored(x, **color_warning)
        logger.warning(fmt(string)) 
    
    def error(string):
        fmt = lambda x: prefix + colored(x, **color_error)
        logger.error(fmt(string)) 

    def user_error(string):
        fmt = lambda x: prefix + colored(x, **color_user_error)
        logger.error(fmt(string)) 
    
    def info(string):
        fmt = lambda x: prefix + colored(x, **color_info)
        logger.info(fmt(string)) 

    def debug(string):
        fmt = lambda x: prefix + colored(x, **color_debug)
        logger.info(fmt(string)) 
     





def semantic_warning(error, element):
    msg = str(error) + '\n' + str(element.where)
    warning(msg)
