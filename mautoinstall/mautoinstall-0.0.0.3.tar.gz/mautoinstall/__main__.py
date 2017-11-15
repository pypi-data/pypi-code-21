"""
Quick install for my apps.
"""
import sys
import os
from os import system, path
import shutil


version = "0.0.0.1"


def main():
    print( "************************************************************************" )
    print( "* THIS SCRIPT WILL INSTALL ALL BITBUCKET.MJR129.TOOLS AND DEPENDENCIES *" )
    print( "************************************************************************" )
    
    print( "CHECKING UNICODE SUPPORT..." )
    
    try:
        print( "😁\r \r", end = "" )
        print( "* NO ERROR 😁" )
    except UnicodeEncodeError as ex:
        print( "\nCHECK FAILED: UnicodeEncodeError" )
        
        print( "** ENTER 'I'GNORE OR 'E'XIT" )
        query = input( "** QUERY: " ).lower()
        
        if query not in ("i", "ignore"):
            print( "USER EXITED - BAD RESPONSE" )
            exit( 1 )
    
    print( "CHECKING COLOUR SUPPORT..." )
    colorterm = os.environ.get( "COLORTERM" )
    
    if colorterm is not None:
        print( "* \033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 128 ) + "m" + "NO ERROR" + "\033[39m" )
    else:
        print( "* \033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "24 BIT RED" + "\033[39m" )
        print( "* " + "\033[31m" + "SYSTEM RED" + "\033[39m" )
        print( "* CHECK FAILED: Not supported" )
        
        print( "** ENTER 'I'GNORE OR 'E'XIT" )
        query = input( "** QUERY: " ).lower()
        
        if query not in ("i", "ignore"):
            print( "USER EXITED - BAD RESPONSE" )
            exit( 1 )
    
    txt = "\033[38;2;" + str( 255 ) + ";" + str( 0 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 255 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 0 ) + "m" + "◢◤" + "\033[39m\033[38;2;" + str( 0 ) + ";" + str( 255 ) + ";" + str( 255 ) + "m" + "◢◤" + "\033[39m"
    print( "┌─────────────────────────────────────┐" )
    print( "│ AUTOMATIC INSTALLER " + version.ljust( 15 ) + " │" )
    print( "├────────────────────────────" + txt + "─┤" )
    
    mode_install: bool = None
    mode_uninstall: bool = None
    mode_reinstall: bool = None
    mode_pip: bool = None
    mode_git: bool = None
    dir_name: str = None
    user_name: str = None
    
    from_pypi = ["PyQt5", "py2neo", "sip", "six", "typing-inspect", "numpy", "neo4j-driver", "jsonpickle", "ete3", "bitarray", "uniprot", "typing", "py-flags", "colorama", "keyring", "biopython"]
    from_bitbucket = ["stringcoercion", "neocommand", "intermake", "mhelper", "editorium", "bio42", "progressivecsv", "cluster_searcher"]
    
    for arg in sys.argv[1:]:  # type:str
        if arg == "--only":
            from_pypi = []
            from_bitbucket = []
        elif arg.startswith( "p+" ):
            from_pypi.append( arg[1:] )
        elif arg.startswith( "b+" ):
            from_bitbucket.append( arg[1:] )
        else:
            print( "BAD COMMAND LINE" )
        exit( 1 )
    
    for package in from_pypi:
        print( "│ " + package.ljust( 36 ) + "│" )
    
    print( "├─────────────────────────────────────┤" )
    
    for package in from_bitbucket:
        print( "│ " + package.ljust( 36 ) + "│" )
    
    print( "└─────────────────────────────────────┘" )
    
    print( "** WHAT DO YOU WANT TO DO, ENTER 'I'NSTALL | 'R'EMOVE | 'U'PGRADE" )
    query = input( "** QUERY: " ).lower()
    
    if query in ("i", "install"):
        print( "INSTALL" )
        mode_install = True
        mode_uninstall = False
        mode_reinstall = False
        pip_args = ""
    elif query in ("r", "remove", "uninstall"):
        print( "REMOVE" )
        mode_install = False
        mode_uninstall = True
        mode_reinstall = False
        pip_args = ""
    elif query in ("u", "upgrade"):
        print( "UPGRADE" )
        mode_install = False
        mode_uninstall = False
        mode_reinstall = True
    else:
        print( "USER EXITED - BAD RESPONSE" )
        exit( 1 )
    
    if mode_install:
        print( "** HOW DO YOU WISH TO INSTALL. ENTER 'U'SER | 'D'EVELOPER." )
        print( "** USER MODE WILL INSTALL VIA PIP (PYPI), DEVELOPER MODE WILL INSTALL VIA GIT (BITBUCKET) AND ALLOW YOU TO MODIFY THE CODE" )
    else:
        print( "** IN WHAT MODE WERE THE PACKAGES INSTALLED. ENTER 'U'SER | 'D'EVELOPER." )
    
    query = input( "** QUERY: " ).lower()
    
    if query in ("u", "user", "p", "pip"):
        print( "USER" )
        mode_pip = True
        mode_git = False
        from_pypi.extend( from_bitbucket )
        from_bitbucket = []
    elif query in ("d", "developer", "g", "git", "b", "bitbucket"):
        print( "DEVELOPER" )
        mode_pip = False
        mode_git = True
    else:
        print( "USER EXITED - BAD RESPONSE" )
        exit( 1 )
    
    if mode_git:
        print( "** ENTER YOUR BITBUCKET USER NAME" )
        query = input( "** QUERY: " )
        
        if not query:
            print( "USER EXITED - BAD RESPONSE" )
            exit( 1 )
        
        user_name = query
        print( "OKAY: " + user_name )
        
        if mode_install:
            print( "** ENTER THE DIRECTORY TO STORE THE GIT REPOSITORIES:" )
        else:
            print( "** ENTER THE DIRECTORY THE EXISTING REPOSITORIES ARE INSTALLED:" )
        
        query = input( "** QUERY: " )
        
        if not query or not path.isdir( query ):
            print( "USER EXITED - BAD RESPONSE" )
            exit( 1 )
        
        dir_name = path.abspath( path.expanduser( query ) )
        print( "OKAY: " + dir_name )
    
    print( "/----------------------------------------------------" )
    print( "| SUMMARY" )
    print( "| VIA PIP IN RELEASE MODE:              " + ", ".join( from_pypi ) )
    print( "| VIA BITBUCKET IN DEVELOPMENT MODE:    " + ", ".join( from_bitbucket ) )
    print( "| GIT USERNAME:                         " + str( user_name ) )
    print( "| TARGET DIRECTORY:                     " + str( dir_name ) )
    print( "| INSTALL:                              " + str( mode_install ) )
    print( "| REINSTALL:                            " + str( mode_reinstall ) )
    print( "| REMOVE:                               " + str( mode_uninstall ) )
    print( "| GIT:                                  " + str( mode_git ) )
    print( "| FORCE_PYPI:                           " + str( mode_pip ) )
    
    print( "** IF THIS IS CORRECT ENTER 'Y'ES:" )
    query = input( "** READY: " ).lower()
    
    if query not in ("y", "yes"):
        print( "USER EXITED - BAD RESPONSE" )
        exit( 1 )
    
    print( "** CONFIRM COMMANDS, ENTER 'Y'ES (DEFAULT) | 'A'LWAYS | 'S'KIP | 'C'ANCEL" )
    
    if from_pypi:
        for VARIABLE in from_pypi:
            print( "**************************** PIP {} ****************************".format( VARIABLE ) )
            
            if mode_install:
                run( "USR", "sudo pip install{}".format( VARIABLE ) )
            elif mode_reinstall:
                run( "US2", "sudo pip install {} --upgrade --force-reinstall".format( VARIABLE ) )
            elif mode_uninstall:
                run( "US3", "sudo pip uninstall {}".format( VARIABLE ) )
            else:
                print( "PROGRAM ERROR - BAD SWITCH 1" )
                exit( 1 )
    
    if from_bitbucket:
        for VARIABLE in from_bitbucket:
            print( "**************************** GIT: {} ****************************".format( VARIABLE ) )
            target_dir = path.join( dir_name, VARIABLE )
            
            if mode_install:
                pass
            elif mode_reinstall:
                run( "REM", "sudo pip uninstall {}".format( VARIABLE ) )
                shutil.rmtree( target_dir )
            elif mode_uninstall:
                run( "REM", "sudo pip uninstall {}".format( VARIABLE ) )
                shutil.rmtree( target_dir )
                continue
            else:
                print( "PROGRAM ERROR - BAD SWITCH 2" )
                exit( 1 )
            
            os.chdir( dir_name )
            if not run( "CLO", "git clone https://{}@bitbucket.org/mjr129/{}.git".format( user_name, VARIABLE ) ):
                continue
            
            os.chdir( target_dir )
            run( "DEV", "sudo pip install -e ." )


__all = set()


def run( id, cmd ):
    print( "** SYSTEM COMMAND: " + cmd )
    
    if id in __all:
        query = "y"
    else:
        query = input( "** QUERY: " ).lower()
    
    if query in ("n", "no", "s", "skip"):
        return False
    elif query in ("y", "yes", "", "all", "a"):
        if query in ("all", "a"):
            __all.add( id )
        
        system( cmd )
        return True
    else:
        print( "USER EXITED - BAD RESPONSE" )
        exit( 1 )


if __name__ == "__main__":
    main()
