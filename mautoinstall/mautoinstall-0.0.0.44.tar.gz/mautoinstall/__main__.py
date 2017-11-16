#! /usr/bin/python

"""
Install helper for my apps with a friendlyish command-line UI.
"""
import sys
import os
from os import system, path
import shutil
import subprocess
import time
import re


SET_ALL = 1
SET_LOCALS = 2
SET_DEPENDENCIES = 3

MODE_INSTALL = 1
MODE_UPGRADE = 2
MODE_UNINSTALL = 3

IMODE_USER = 1
IMODE_DEVELOPER = 2

DIM = "\033[2m"
FORE_BLUE = "\033[34m"
BACK_BLUE = "\033[44m"
BACK_BRIGHT_BLACK = "\033[100m"
FORE_BRIGHT_WHITE = "\033[1;37m"
BACK_BRIGHT_WHITE = "\033[107m"
FORE_BRIGHT_RED = "\033[1;31m"
FORE_BLACK = "\033[30m"
RESET = "\033[0m"
BOX = RESET + BACK_BRIGHT_WHITE + FORE_BLACK
MY_VERSION = "0.0.0.44"
CONSOLE_WIDTH = max( 10, shutil.get_terminal_size()[0] - 1 )


class UserExitError( Exception ):
    pass


class BadConfigError( Exception ):
    pass


def main():
    """
    Exit codes: 0 = good, 1 = user error, 2 = keyboard quit, 3 = config error
    :return: 
    """
    code = 2
    
    try:
        code = __main()
    except UserExitError:
        code = 1
    except KeyboardInterrupt:
        code = 2
    except BadConfigError:
        code = 3
    except:
        raise
    finally:
        print( RESET + "EXIT CODE {}".format( code ) )
    
    exit( code )


class Settings:
    def __init__( self ):
        self.from_pypi = ["setuptools", "PyQt5", "py2neo", "sip", "six", "typing-inspect", "numpy", "neo4j-driver", "jsonpickle", "ete3", "bitarray", "uniprot", "typing", "py-flags", "colorama", "keyring", "biopython"]
        self.from_bitbucket = ["stringcoercion", "neocommand", "intermake", "mhelper", "editorium", "bio42", "progressivecsv", "cluster_searcher", "groot"]
        self.get_pip = None
        self.python_interpreter = None
        self.mode_operation = None
        self.mode_user = None
        self.user_name = None
        self.dir_name = None
        self.mode_set = None
        self.always_yes = set()
        self.quiet = False
        self.ignore_warnings = False


settings = Settings()


def __main():
    __query_runtime_version()
    __query_command_line()
    __query_unicode_support()
    __query_colour_support()
    
    if settings.get_pip:
        __install_pip( settings.python_interpreter )
        return 0
    
    __query_python_interpreter()
    __check_python_interpreter()
    __query_mode_set()
    __query_procedure()
    __query_mode_user()
    
    if settings.mode_set == SET_LOCALS:
        settings.from_pypi.clear()
    
    if settings.mode_user == IMODE_USER:
        settings.from_pypi.extend( settings.from_bitbucket )
        settings.from_bitbucket = []
    
    if settings.mode_user == IMODE_DEVELOPER:
        __query_user_name()
        __query_target_directory()
    
    __query_summary()
    
    __install_git()
    
    __install_bitbucket()
    
    return 0


def __install_git():
    if not settings.from_pypi:
        return
    
    __print_top()
    __print_line( "CONFIRM PIP COMMANDS, ENTER «Y»ES (DEFAULT) | «A»LWAYS | «S»KIP | «C»ANCEL" )
    __print_bottom()
    
    for VARIABLE in settings.from_pypi:
        __print_top()
        __print_line( "INSTALL «{}» VIA PIP".format( VARIABLE ) )
        
        if settings.mode_operation == MODE_INSTALL:
            __run( "USR", "sudo {} -m pip install {}".format( settings.python_interpreter, VARIABLE ) )
        elif settings.mode_operation == MODE_UPGRADE:
            __run( "US2", "sudo {} -m pip install {} --upgrade --force-reinstall".format( settings.python_interpreter, VARIABLE ) )
        elif settings.mode_operation == MODE_UNINSTALL:
            __run( "US3", "sudo {} -m pip uninstall {}".format( settings.python_interpreter, VARIABLE ) )


def __install_bitbucket():
    if not settings.from_bitbucket:
        return
    
    __print_top()
    __print_line( "CONFIRM GIT COMMANDS, ENTER «Y»ES (DEFAULT) | «A»LWAYS | «S»KIP | «C»ANCEL" )
    __print_bottom()
    
    for VARIABLE in settings.from_bitbucket:
        target_dir = path.join( settings.dir_name, VARIABLE )
        
        if settings.mode_operation == MODE_INSTALL:
            pass
        elif settings.mode_operation == MODE_UPGRADE or settings.mode_operation == MODE_UNINSTALL:
            if path.isdir( target_dir ):
                if not __rmdir( target_dir ):
                    continue
        
        __print_top()
        __print_line( "DOWNLOAD «{}» FROM BITBUCKET".format( VARIABLE ) )
        os.chdir( settings.dir_name )
        if not __run( "CLO", "git clone https://{}@bitbucket.org/mjr129/{}.git".format( settings.user_name, VARIABLE ) ):
            continue
        
        os.chdir( target_dir )
        __print_top()
        __print_line( "INSTALL «{}» FROM LOCAL FOLDER".format( VARIABLE ) )
        __run( "DEV", "sudo {} -m pip install -e .".format( settings.python_interpreter ) )


def __install_pip( python_interpreter ):
    print( "OBTAINING PIP..." )
    os.system( "wget https://bootstrap.pypa.io/get-pip.py" )
    os.system( "{} get-pip.py".format( python_interpreter ) )
    os.remove( "get-pip.py" )


def __query_command_line():
    def __raise_error( x ):
        print( "BAD COMMAND LINE: " + x )
        raise BadConfigError()
    
    
    cmd_mode = __raise_error
    
    for arg in sys.argv[1:]:  # type:str
        if arg == "--help":
            print( "--help                      this message" )
            print( "--clear-pip                 clear pip list" )
            print( "--clear-git                 clear git list" )
            print( "--dir <directory>           set target directory" )
            print( "--get-pip                   install pip first" )
            print( "--git <package> ...         add to git list" )
            print( "--operation <mode>          set operation mode" )
            print( "--pip <package> ...         add to pip list" )
            print( "--set <mode>                set set mode" )
            print( "--user <mode>               set user mode" )
            print( "--python <interpreter>      set python interpreter" )
            print( "--name <username>           set user name" )
            print( "--quiet                     don't ask confirm-type questions" )
            print( "--nowarn                    ignore colour warning" )
            raise UserExitError()
        elif arg == "--clear-pip":
            settings.from_pypi.clear()
        elif arg == "--clear-git":
            settings.from_bitbucket.clear()
        elif arg == "--dir":
            cmd_mode = lambda x: setattr( settings, "dir_name", x )
        elif arg == "--get-pip":
            settings.get_pip = True
        elif arg == "--git" or arg == "--bitbucket":
            cmd_mode = lambda x: settings.from_bitbucket.append( x )
        elif arg == "--operation":
            cmd_mode = lambda x: setattr( settings, "mode_operation", int( x ) )
        elif arg == "--pip" or arg == "--pypi":
            cmd_mode = lambda x: settings.get_pip.append( x )
        elif arg == "--set":
            cmd_mode = lambda x: setattr( settings, "mode_set", int( x ) )
        elif arg == "--user":
            cmd_mode = lambda x: setattr( settings, "mode_user", int( x ) )
        elif arg == "--python":
            cmd_mode = lambda x: setattr( settings, "python_interpreter", x )
        elif arg == "--name":
            cmd_mode = lambda x: setattr( settings, "user_name", x )
        elif arg == "--quiet":
            settings.quiet = True
        elif arg == "--nowarn":
            settings.ignore_warnings = True
        else:
            cmd_mode( arg )


def __query_runtime_version():
    version = sys.version_info
    
    if version[0] != 3 or version[1] < 6:
        print( "YOU ARE USING PYTHON VERSION {}.{}, BUT THIS APPLICATION REQUIRES VERSION 3.6.".format( version[0], version[1] ) )
        raise BadConfigError()
    
    print( "MAUTOINSTALL VERSION " + MY_VERSION + ". PYTHON VERSION " + ".".join( str( x ) for x in version ) )


def __query_unicode_support():
    try:
        print( "😁\r \r", end = "" )
    except UnicodeEncodeError:
        print( "UNICODE CHECK FAILED. YOU ARE NOT USING A UNICODE TERMINAL OR UNICODE IS MISCONFIGURED." )
        print( "PLEASE SWITCH TO A UNICODE TERMINAL OR ENABLE UNICODE." )
        print( "PROGRAM EXITED - NOT SUPPORTED" )
        raise BadConfigError()


def __query_colour_support():
    colorterm = os.environ.get( "COLORTERM" )
    
    if colorterm is None:
        __print_top()
        __print_line( "CHECKING COLOUR SUPPORT..." )
        __print_line( "\033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "24 BIT RED" + BOX )
        __print_line( "\033[31m" + "SYSTEM RED" + BOX )
        __print_line( "CHECK FAILED: YOU ARE NOT USING A TRUE COLOUR TERMINAL OR TRUE COLOUR" )
        __print_line( "IS MISCONFIGURED." )
        __print_line( "PLEASE SWITCH A TRUE COLOUR TERMINAL OR ENABLE 'COLORTERM'." )
        __print_line( "IF YOU ARE USING SSH THIS WARNING MAY BE IN ERROR'." )
        
        if not settings.ignore_warnings and not settings.quiet:
            __print_middle()
            __print_line( "ENTER 'I'GNORE OR 'E'XIT" )
            query = __input( "QUERY: " ).lower()
            
            if query not in ("i", "ignore"):
                __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
                __print_bottom()
                raise UserExitError()
        
        __print_bottom()


def __query_summary():
    __print_top()
    __print_line( "SUMMARY" )
    __print_middle()
    __print_line( "VIA PIP IN RELEASE MODE:              " + str( len( settings.from_pypi ) ) + " PACKAGES" )
    __print_line( "VIA BITBUCKET IN DEVELOPMENT MODE:    " + str( len( settings.from_bitbucket ) ) + " PACKAGES" )
    __print_line( "GIT USERNAME:                         " + str( settings.user_name ) )
    __print_line( "TARGET DIRECTORY:                     " + str( settings.dir_name ) )
    __print_line( "INSTALL:                              " + str( settings.mode_operation == MODE_INSTALL ) )
    __print_line( "REINSTALL:                            " + str( settings.mode_operation == MODE_UPGRADE ) )
    __print_line( "REMOVE:                               " + str( settings.mode_operation == MODE_UNINSTALL ) )
    __print_line( "USER MODE:                            " + str( settings.mode_user == IMODE_USER ) )
    __print_line( "DEVELOPER MODE:                       " + str( settings.mode_user == IMODE_DEVELOPER ) )
    __print_line( "PYTHON INTERPRETER                    " + str( settings.python_interpreter ) )
    
    if not settings.quiet:
        __print_middle()
        __print_line( "IF THIS IS CORRECT ENTER «Y»ES:" )
        query = __input( "CONFIRM" ).lower()
        if query not in ("y", "yes"):
            __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
            __print_bottom()
            raise UserExitError()
    
    __print_bottom()


def __query_target_directory():
    if settings.dir_name:
        return
    
    __print_top()
    if settings.mode_operation == MODE_INSTALL:
        __print_line( "ENTER THE «DIRECTORY» TO STORE THE GIT REPOSITORIES:" )
    else:
        __print_line( "ENTER THE «DIRECTORY» THE EXISTING REPOSITORIES ARE INSTALLED:" )
    query = __input( "DIRECTORY" )
    if not query:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    
    settings.dir_name = path.abspath( path.expanduser( query ) )
    
    if not path.isdir( settings.dir_name ):
        __print_line( "USER EXITED - NO SUCH FOLDER AS «{}»".format( settings.dir_name ) )
        __print_bottom()
        raise UserExitError()
    
    __print_line( "OKAY: " + settings.dir_name )
    __print_bottom()


def __query_user_name():
    if settings.user_name:
        return
    
    __print_top()
    __print_line( "ENTER YOUR BITBUCKET «USER NAME»" )
    query = __input( "USER NAME" )
    if not query:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    settings.user_name = query
    __print_line( "OKAY: " + settings.user_name )
    __print_bottom()


def __query_mode_set():
    if settings.mode_set:
        return
    
    __print_top()
    __print_line( "" )
    __print_line( "AUTOMATIC INSTALLER " + MY_VERSION.ljust( 15, " " ) )
    __print_line( "" )
    __print_zx_middle()
    
    __print_line( "" )
    __print_line( "DEPENDENCIES:" )
    __print_line( "" )
    for package in settings.from_pypi:
        __print_line( package )
    
    __print_line( "" )
    __print_middle()
    __print_line( "" )
    __print_line( "LOCALS:" )
    __print_line( "" )
    for package in settings.from_bitbucket:
        __print_line( package )
    __print_line( "" )
    __print_middle()
    __print_line( "" )
    __print_line( "WHAT SET DO YOU WISH TO USE: «A»LL | «D»EPENDENCIES | «L»OCALS" )
    __print_line( "AS LISTED ABOVE. IF UNSURE SELECT «ALL»." )
    
    query = __input( "SET" ).lower()
    
    if query in ("a", "all"):
        __print_line( "ALL" )
        settings.mode_set = SET_ALL
    elif query in ("d", "dependencies"):
        __print_line( "DEPENDENCIES" )
        settings.mode_set = SET_DEPENDENCIES
    elif query in ("l", "locals"):
        __print_line( "LOCALS" )
        settings.mode_set = SET_LOCALS
    else:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    
    __print_bottom()
    return settings.mode_set


def __query_mode_user():
    if settings.mode_user:
        return
    
    __print_top()
    
    if settings.mode_operation == MODE_INSTALL:
        __print_line( "HOW DO YOU WISH TO INSTALL: «U»SER | «D»EVELOPER" )
        __print_line( "USER MODE WILL INSTALL VIA PIP (PYPI), DEVELOPER MODE WILL" )
        __print_line( "INSTALL VIA GIT (BITBUCKET) AND ALLOW YOU TO MODIFY THE CODE" )
    else:
        __print_line( "IN WHAT MODE WERE THE PACKAGES INSTALLED. ENTER «U»SER | «D»EVELOPER." )
    
    query = __input( "MODE" ).lower()
    if query in ("u", "user", "p", "pip"):
        __print_line( "USER" )
        settings.mode_user = IMODE_USER
    elif query in ("d", "developer"):
        __print_line( "DEVELOPER" )
        settings.mode_user = IMODE_DEVELOPER
    else:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    
    __print_bottom()


def __query_procedure():
    __print_top()
    __print_line( "WHAT DO YOU WANT TO DO, ENTER «I»NSTALL | «R»EMOVE | «U»PGRADE" )
    query = __input( "MODE" ).lower()
    if query in ("i", "install"):
        __print_line( "INSTALL" )
        settings.mode_operation = MODE_INSTALL
    elif query in ("r", "remove", "uninstall"):
        __print_line( "REMOVE" )
        settings.mode_operation = MODE_UNINSTALL
    elif query in ("u", "upgrade"):
        __print_line( "UPGRADE" )
        settings.mode_operation = MODE_UPGRADE
    else:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    __print_bottom()


def __check_python_interpreter():
    output = __check_interpreter( settings.python_interpreter )
    
    if not output:
        __print_top()
        __print_line( "CHECKING PYTHON INTERPRETER..." )
        __print_line( "CHECK FAILED. THE «{}» COMMAND IS NOT BOUND TO PYTHON".format( settings.python_interpreter ) )
        __print_line( "THIS APPLICATION REQUIRES PYTHON VERSION 3.6." )
        __print_bottom()
        raise BadConfigError()
    
    if output < 3.6:
        __print_top()
        __print_line( "CHECKING PYTHON INTERPRETER..." )
        __print_line( "CHECK FAILED. THE «{}» COMMAND IS BOUND TO PYTHON VERSION «{}»".format( settings.python_interpreter, output ) )
        __print_line( "THIS APPLICATION REQUIRES PYTHON VERSION 3.6." )
        __print_bottom()
        raise BadConfigError()


def __check_interpreter( python_interpreter ):
    try:
        output = subprocess.check_output( [python_interpreter, "--version"] ).decode().split( " ", 1 )[1].strip().split( "." )
        return int( output[0] ) + int( output[1] ) / 10
    except:
        return 0


def __query_python_interpreter():
    if settings.python_interpreter:
        return
    
    for test in (sys.executable, "python", "python3", "python3.6"):
        if __check_interpreter( test ) >= 3.6:
            settings.python_interpreter = test
            return test
    
    __print_top()
    __print_line( "TRYING TO FIND PYTHON 3.6 OR ABOVE" )
    __print_line( "FAILED TO FIND AUTOMATICALLY" )
    
    __print_middle()
    __print_line( "SPECIFY THE COMMAND YOU USE TO START YOUR «PYTHON INTERPRETER»" )
    __print_line( "THIS IS USUALLY «python», BUT IF YOU HAVE MULTIPLE VERSIONS OF PYTHON" )
    __print_line( "INSTALLED THIS MAY BE «python3» OR «python3.6»." )
    query = __input( "INTERPRETER" )
    if not query:
        __print_line( "USER EXITED - THE TEXT «{}» IS NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        raise UserExitError()
    
    settings.python_interpreter = query


def __print_top():
    for n in range( 5 ):
        print()
        __eol()
    
    print()
    print( BOX + "┌────────────────────────────────────────────────────────────────────────────────┐" + RESET )
    __eol()


def __print_middle():
    print( BOX + "├────────────────────────────────────────────────────────────────────────────────┤" + RESET )
    __eol()


def __print_zx_middle():
    txt = "\033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 255 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 255 ) + "m" + "◢◤" + BOX
    print( BOX + "├───────────────────────────────────────────────────────────────────────" + txt + "─┤" + RESET )
    __eol()


def __print_line( text ):
    pad_text = text.replace( "«", "" ).replace( "»", "" )
    pad_text = re.sub( "\x1b\[[0-9;]*m", "", pad_text )
    pad = 78 - len( pad_text )
    text = text.replace( "«", FORE_BRIGHT_RED ).replace( "»", BOX )
    print( BOX + "│ " + text + (" " * pad) + " │" + RESET )
    __eol()


def __eol( bottom = False ):
    if bottom:
        time.sleep( 0.250 )
    else:
        time.sleep( 0.01 )


def __print_bottom():
    print( BOX + "└────────────────────────────────────────────────────────────────────────────────┘" + RESET )
    __eol( True )


def __print_bar():
    print()


def __rmdir( dir ):
    id = "RMD"
    
    __print_top()
    __print_line( "REMOVE DIRECTORY: " + dir )
    
    if settings.quiet or id in settings.always_yes:
        query = "y"
    else:
        query = __input( "CONFIRM" )
    
    if query in ("n", "no", "s", "skip"):
        __print_line( "SKIPPED BY USER" )
        __print_bottom()
        return False
    elif query in ("y", "yes", "", "all", "a"):
        __print_bottom()
        
        if query in ("all", "a"):
            settings.always_yes.add( id )
        
        shutil.rmtree( dir )
        return True
    else:
        __print_line( "USER EXITED - «{}» NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        exit( 1 )


def __run( id, cmd ):
    __print_middle()
    __print_line( "SYSTEM COMMAND: " + cmd )
    
    if settings.quiet or id in settings.always_yes:
        query = "y"
    else:
        query = __input( "CONFIRM" )
    
    if query in ("n", "no", "s", "skip"):
        __print_line( "SKIPPED BY USER" )
        __print_bottom()
        return False
    elif query in ("y", "yes", "", "all", "a"):
        __print_bottom()
        
        if query in ("all", "a"):
            settings.always_yes.add( id )
        
        system( cmd )
        return True
    else:
        __print_line( "USER EXITED - «{}» NOT RECOGNISED".format( query or '""' ) )
        __print_bottom()
        exit( 1 )


def __input( query ):
    text = "│ " + query + ": "
    print( BOX + text.ljust( 80, " " ) + " │" + RESET, end = "\r" )
    print( BOX + text + RESET, end = FORE_BRIGHT_RED )
    result = input( )
    print( RESET, end = "" )
    return result


if __name__ == "__main__":
    main()
