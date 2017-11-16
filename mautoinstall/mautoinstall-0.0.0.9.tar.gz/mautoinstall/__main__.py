#! /usr/bin/python

"""
Quick install for my apps.
"""
import sys
import os
from os import system, path
import shutil
import subprocess


DIM = "\033[2m"
BACK_BLUE = "\033[44m"
BACK_BRIGHT_BLACK = "\033[100m"
FORE_BRIGHT_WHITE = "\033[1;37m"
BACK_BRIGHT_WHITE = "\033[107m"
FORE_BRIGHT_RED = "\033[1;31m"
FORE_BLACK = "\033[30m"
RESET = "\033[0m"
BOX = RESET + BACK_BRIGHT_WHITE + FORE_BLACK
my_version = "0.0.0.9"
console_width = max( 10, shutil.get_terminal_size()[0] - 1 )


def main() -> None:
    """
    Exit codes: 0 = good, 1 = user error, 2 = program error
    :return: 
    """
    code = 2
    
    try:
        code = __main()
    except KeyboardInterrupt:
        code = 1
    except:
        raise
    finally:
        __print( RESET + "EXIT CODE {}".format( code ) )
    
    exit( code )


def __main() -> int:
    from_pypi = ["PyQt5", "py2neo", "sip", "six", "typing-inspect", "numpy", "neo4j-driver", "jsonpickle", "ete3", "bitarray", "uniprot", "typing", "py-flags", "colorama", "keyring", "biopython"]
    from_bitbucket = ["stringcoercion", "neocommand", "intermake", "mhelper", "editorium", "bio42", "progressivecsv", "cluster_searcher"]
    python_interpreter = "python3"
    cmd_mode = 0
    get_pip = False
    
    for arg in sys.argv[1:]:  # type:str
        if arg == "--only":
            from_pypi.clear()
            from_bitbucket.clear()
        elif arg == "--pip" or arg == "--pypi":
            cmd_mode = 1
        elif arg == "--git" or arg == "--bitbucket":
            cmd_mode = 2
        elif arg == "--python":
            cmd_mode = 3
        elif arg == "--get-pip":
            get_pip = True
        elif cmd_mode == 1:
            from_pypi.append( arg[1:] )
        elif cmd_mode == 2:
            from_bitbucket.append( arg[1:] )
        elif cmd_mode == 3:
            python_interpreter = arg
            cmd_mode = 0
        else:
            __print( "BAD COMMAND LINE" )
            return 1
    
    for n in range( 100 ):
        print()
    
    if get_pip:
        print( "OBTAINING PIP..." )
        os.system( "wget https://bootstrap.pypa.io/get-pip.py" )
        os.system( "{} get-pip.py".format( python_interpreter ) )
        os.remove( "get-pip.py" )
        return 0
    
    __print( "************************************************************************" )
    __print( "* THIS SCRIPT WILL INSTALL ALL BITBUCKET.MJR129.TOOLS AND DEPENDENCIES *" )
    __print( "************************************************************************" )
    
    __print( "CHECKING PYTHON VERSION..." )
    
    version = sys.version_info
    
    if version[0] != 3 and version[1] < 6:
        __print( "CHECK FAILED. YOU ARE USING PYTHON VERSION {}.{}, BUT THIS APPLICATION REQUIRES VERSION 3.6.".format( version[0], version[1] ) )
        return 1
    
    __print( "* NO ERROR " + ".".join( str( x ) for x in version ) )
    
    __print( "CHECKING UNICODE SUPPORT..." )
    
    try:
        print( "😁\r \r", end = "" )
        __print( "* NO ERROR 😁" )
    except UnicodeEncodeError:
        __print( "CHECK FAILED. YOU ARE NOT USING A UNICODE TERMINAL OR UNICODE IS MISCONFIGURED." )
        __print( "PLEASE SWITCH TO A UNICODE TERMINAL OR ENABLE UNICODE." )
        __print( "PROGRAM EXITED - NOT SUPPORTED" )
        return 1
    
    __print( "CHECKING COLOUR SUPPORT..." )
    colorterm = os.environ.get( "COLORTERM" )
    
    if colorterm is not None:
        __print( "* \033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 128 ) + "m" + "NO ERROR" + RESET )
    else:
        __print( "* \033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "24 BIT RED" + RESET )
        __print( "* " + "\033[31m" + "SYSTEM RED" + RESET )
        __print( "CHECK FAILED: YOU ARE NOT USING A TRUE COLOUR TERMINAL OR TRUE COLOUR IS MISCONFIGURED." )
        __print( "PLEASE SWITCH A TRUE COLOUR TERMINAL OR ENABLE 'COLORTERM'." )
        __print( "IF YOU ARE USING SSH THIS ASSERTION MAY BE IN ERROR'." )
        
        __print( "** ENTER 'I'GNORE OR 'E'XIT" )
        query = input( "QUERY: " ).lower()
        
        if query not in ("i", "ignore"):
            __print( "USER EXITED - BAD RESPONSE" )
            return 1
    
    __print_bar()
    
    __print( "CHECKING PYTHON INTERNAL..." )
    
    output = subprocess.check_output( [python_interpreter, "--version"] ).decode().split( " ", 1 )[1].strip().split( "." )
    
    if int( output[0] ) != 3 and int( output[1] ) < 6:
        __print( "CHECK FAILED. THE 'PYTHON' COMMAND IS BOUND TO PYTHON VERSION {}.{}, BUT THIS APPLICATION REQUIRES VERSION 3.6.".format( output[0], output[1] ) )
        return 1
    
    txt = "\033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 255 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 255 ) + "m" + "◢◤" + BOX
    __print( BOX + "┌─────────────────────────────────────┐" + RESET )
    __print( BOX + "│ AUTOMATIC INSTALLER " + my_version.ljust( 15, " " ) + " │" + RESET )
    __print( BOX + "├────────────────────────────" + txt + "─┤" + RESET )
    
    dir_name: str = None
    user_name: str = None
    
    for package in from_pypi:
        __print( BOX + "│ " + package.ljust( 36, " " ) + "│" + RESET )
    
    __print( BOX + "├─────────────────────────────────────┤" + RESET )
    
    for package in from_bitbucket:
        __print( BOX + "│░" + package.ljust( 36, " " ) + "│" + RESET )
    
    __print( BOX + "└─────────────────────────────────────┘" + RESET )
    
    __print_top()
    __print_line( "WHAT DO YOU WANT TO DO, ENTER «I»NSTALL | «R»EMOVE | «U»PGRADE" )
    query = __input( "MODE" ).lower()
    
    if query in ("i", "install"):
        __print_line( "INSTALL" )
        mode_install = True
        mode_uninstall = False
        mode_reinstall = False
    elif query in ("r", "remove", "uninstall"):
        __print_line( "REMOVE" )
        mode_install = False
        mode_uninstall = True
        mode_reinstall = False
    elif query in ("u", "upgrade"):
        __print_line( "UPGRADE" )
        mode_install = False
        mode_uninstall = False
        mode_reinstall = True
    else:
        __print_line( "USER_EXITED - BAD RESPONSE" )
        __print_bottom()
        return 1
    
    __print_bottom()
    
    if mode_install:
        __print_top()
        __print_line( "HOW DO YOU WISH TO INSTALL. ENTER «U»SER | «D»EVELOPER." )
        __print_line( "USER MODE WILL INSTALL VIA PIP (PYPI), DEVELOPER MODE WILL" )
        __print_line( "INSTALL VIA GIT (BITBUCKET) AND ALLOW YOU TO MODIFY THE CODE" )
    else:
        __print_line( "IN WHAT MODE WERE THE PACKAGES INSTALLED. ENTER 'U'SER | 'D'EVELOPER." )
    
    query = __input( "MODE" ).lower()
    
    if query in ("u", "user", "p", "pip"):
        __print_line( "USER" )
        mode_pip = True
        mode_git = False
        from_pypi.extend( from_bitbucket )
        from_bitbucket = []
    elif query in ("d", "developer", "g", "git", "b", "bitbucket"):
        __print_line( "DEVELOPER" )
        mode_pip = False
        mode_git = True
    else:
        __print_line( "USER EXITED - BAD RESPONSE" )
        __print_bottom()
        return 1
    
    __print_bottom()
    
    if mode_git:
        __print_top()
        __print_line( "ENTER YOUR BITBUCKET «USER NAME»" )
        query = __input( "USER NAME" )
        
        if not query:
            __print_line( "USER EXITED - BAD RESPONSE" )
            __print_top()
            return 1
        
        user_name = query
        __print_line( "OKAY: " + user_name )
        
        __print_middle()
        
        if mode_install:
            __print_line( "ENTER THE «DIRECTORY» TO STORE THE GIT REPOSITORIES:" )
        else:
            __print_line( "ENTER THE «DIRECTORY» THE EXISTING REPOSITORIES ARE INSTALLED:" )
        
        query = __input( "DIRECTORY" )
        
        if not query or not path.isdir( query ):
            __print_line( "USER EXITED - BAD RESPONSE" )
            __print_bottom()
            return 1
        
        dir_name = path.abspath( path.expanduser( query ) )
        __print_line( "OKAY: " + dir_name )
        __print_bottom()
    
    __print_top()
    __print_line( "SUMMARY" )
    __print_middle()
    __print_line( "VIA PIP IN RELEASE MODE:              " + ", ".join( from_pypi ) )
    __print_line( "VIA BITBUCKET IN DEVELOPMENT MODE:    " + ", ".join( from_bitbucket ) )
    __print_line( "GIT USERNAME:                         " + str( user_name ) )
    __print_line( "TARGET DIRECTORY:                     " + str( dir_name ) )
    __print_line( "INSTALL:                              " + str( mode_install ) )
    __print_line( "REINSTALL:                            " + str( mode_reinstall ) )
    __print_line( "REMOVE:                               " + str( mode_uninstall ) )
    __print_line( "GIT:                                  " + str( mode_git ) )
    __print_line( "FORCE_PYPI:                           " + str( mode_pip ) )
    __print_middle()
    __print_line( "IF THIS IS CORRECT ENTER «Y«ES:" )
    query = __input( "CONFIRM" ).lower()
    
    if query not in ("y", "yes"):
        __print_line( "USER EXITED - BAD RESPONSE" )
        __print_bottom()
        return 1
    
    __print_bottom()
    
    __print_top()
    __print_line( "CONFIRM COMMANDS, ENTER «Y»ES (DEFAULT) | «A»LWAYS | «S»KIP | «C»ANCEL" )
    
    if from_pypi:
        for VARIABLE in from_pypi:
            __print_middle()
            __print_line( "I WILL NOW INSTALL «{}» VIA PIP".format( VARIABLE ) )
            
            if mode_install:
                __run( "USR", "sudo {} -m pip install{}".format( python_interpreter, VARIABLE ) )
            elif mode_reinstall:
                __run( "US2", "sudo {} -m pip install {} --upgrade --force-reinstall".format( python_interpreter, VARIABLE ) )
            elif mode_uninstall:
                __run( "US3", "sudo {} -m pip uninstall {}".format( python_interpreter, VARIABLE ) )
            else:
                __print( "PROGRAM ERROR - BAD SWITCH 1" )
                return 1
    
    if from_bitbucket:
        for VARIABLE in from_bitbucket:
            __print_middle()
            __print_line( "I WILL NOW DOWNLOAD «{}» FROM BITBUCKET".format( VARIABLE ) )
            target_dir = path.join( dir_name, VARIABLE )
            
            if mode_install:
                pass
            elif mode_reinstall:
                __run( "REM", "sudo {} -m pip uninstall {}".format( python_interpreter, VARIABLE ) )
                shutil.rmtree( target_dir )
            elif mode_uninstall:
                __run( "REM", "sudo {} -m pip uninstall {}".format( python_interpreter, VARIABLE ) )
                shutil.rmtree( target_dir )
                continue
            else:
                __print( "PROGRAM ERROR - BAD SWITCH 2" )
                return 1
            
            os.chdir( dir_name )
            if not __run( "CLO", "git clone https://{}@bitbucket.org/mjr129/{}.git".format( user_name, VARIABLE ) ):
                continue
            
            os.chdir( target_dir )
            __run( "DEV", "sudo {} -m pip install -e .".format( python_interpreter ) )
    
    __print_bottom()
    __print_bar()
    
    return 0


def __print_top():
    print()
    print( BOX + "┌────────────────────────────────────────────────────────────────────────────┐" + RESET )


def __print_middle():
    print( BOX + "├────────────────────────────────────────────────────────────────────────────┤" + RESET )


def __print_line( text ):
    pad = 74 - len( text.replace( "«", "" ).replace( "»", "" ) )
    text = text.replace( "«", FORE_BRIGHT_RED ).replace( "»", BOX )
    print( BOX + "│ " + text + (" " * pad) + " │" )


def __print_bottom():
    print( BOX + "└────────────────────────────────────────────────────────────────────────────┘" + RESET )


def __print_bar():
    print()


__all = set()


def __run( id, cmd ):
    __print_line( "SYSTEM COMMAND: " + cmd )
    
    if id in __all:
        query = "y"
    else:
        query = __input( "CONFIRM" )
    
    if query in ("n", "no", "s", "skip"):
        return False
    elif query in ("y", "yes", "", "all", "a"):
        if query in ("all", "a"):
            __all.add( id )
        
        system( cmd )
        return True
    else:
        __print_line( "USER EXITED - BAD RESPONSE" )
        __print_bottom()
        exit( 1 )


def __input( query ):
    text = "│ " + query + ": "
    print( text.ljust( 76, " " ) + " │", end = "\r" )
    result = input( text )
    sys.stdout.flush()
    return result


def __print( text ):
    print( text )


if __name__ == "__main__":
    main()
