"""
Provides a command-line based front-end.

This is only a simple, example front end, the Python Interactive Interface provides a similar interface with more features.
"""
import os
import shlex
import warnings
from os import path
from typing import Callable, Dict, List, Optional

import sys
from colorama import Fore, Style, Back

from intermake.engine import constants
from intermake.engine.constants import EStream
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin, PluginArg
from intermake.hosts.base import ERunMode, RunHostArgs
from intermake.hosts.console import UserExitError
from mhelper import file_helper, string_helper
from mhelper.string_helper import FindError


__author__ = "Martin Rusilowicz"

__save_history_function = None  # type: Callable[[],None]


def find_command( text: str, plugin_type: type = None ):
    """
    Finds the command with the name.
    :param text: 
    :param plugin_type: 
    :return:
    :except FindError: Find failed. 
    """
    source_list = MENV.plugins.all_plugins()
    
    if plugin_type:
        source_list = [x for x in source_list if isinstance( x, plugin_type )]
    
    host = MENV.host
    text = host.translate_name( text )
    
    
    def ___get_names( plugin: Plugin ):
        return [host.translate_name( x ) for x in plugin.names]
    
    
    return string_helper.find( source = source_list,
                               search = text,
                               namer = ___get_names,
                               detail = "plugin",
                               fuzzy = True )


class CliSyntaxError( Exception ):
    pass


def __execute_command( arguments: List[str] ) -> None:
    """
    Executes a command
    :param arguments: See Plugins.Commands.general_help() for a description of what we parse. 
    """
    # No arguments means do nothing
    if len( arguments ) == 0 or (len( arguments ) == 1 and not arguments[0]):
        return
    
    # ":" means we will perform 2 commands, so split about the ":" and repeat
    if ":" in arguments:
        i = arguments.index( ":" )
        left = arguments[0:i]
        right = arguments[(i + 1):]
        __execute_command( left )
        __execute_command( right )
        return
    
    # Get the command name (first argument)
    cmd = arguments[0]
    
    arguments = arguments[1:]
    
    # Find the plugin we are going to run
    try:
        plugin = find_command( cmd )  # type: Plugin
    except FindError as ex:
        raise CliSyntaxError( "The plugin «{}» does not exist.".format( cmd ) ) from ex
    
    # Create the parameters
    args = []  # type: List[Optional[object]]
    kwargs = { }  # type: Dict[str,Optional[object]]
    
    host = MENV.host
    
    for arg_text in arguments:
        # "+" and "-" mean assign a keyword argument to true/False  
        if arg_text.startswith( "+" ):
            arg_text = arg_text[1:] + "=True"
        elif arg_text.startswith( "-" ):
            arg_text = arg_text[1:] + "=False"
        
        # "=" means a keyword argument
        if "=" in arg_text:
            k, v = arg_text.split( "=", 1 )
            if k in kwargs:
                raise CliSyntaxError( "The key «{0}» has been specified more than once.".format( k ) )
            
            try:
                plugin_arg = string_helper.find(
                        source = plugin.args,
                        search = host.translate_name( k ),
                        namer = lambda x: host.translate_name( x.name ),
                        detail = "argument" )  # type: PluginArg
            except FindError as ex:
                raise CliSyntaxError( "Cannot find argument «{}» in «{}».".format( k, plugin ) ) from ex
            
            if plugin_arg is None:
                raise CliSyntaxError( "The plugin «{}» does not have an argument named «{}» or similar. The available arguments are: {}".format( plugin.name, k, ", ".join( x.name for x in plugin.args ) ) )
            
            kwargs[plugin_arg.name] = __convert_string( plugin_arg, plugin, v )
        else:
            # Everything else is a positional argument
            if kwargs:
                raise CliSyntaxError( "A positional parameter (in this case «{0}») cannot be specified after named parameters.".format( arg_text ) )
            
            if len( args ) == len( plugin.args ):
                raise CliSyntaxError( "Too many arguments specified for «{}», which takes {}.".format( plugin, len( plugin.args ) ) )
            
            plugin_arg = plugin.args[len( args )]
            
            args.append( __convert_string( plugin_arg, plugin, arg_text ) )
    
    plugin.run( *args, **kwargs )


def __convert_string( arg, plugin, value: str ):
    value = string_helper.unescape( value )
    
    import stringcoercion
    try:
        result = stringcoercion.get_default_coercer().coerce( arg.type, value )
        return result
    except Exception as ex:
        raise CliSyntaxError( "Value «{}» rejected for argument «{}»::«{}».".format( value, plugin, arg ) ) from ex


def __begin_readline() -> Optional[Callable[[], None]]:
    """
    Starts readline (the root that allows a UNIX terminal to accept things besides basic text).
    It doesn't work on Windows, or even some UNIX some platforms, which is why its got to be quarantined here.
    Returns a function that can be called to save the history on program termination.
    """
    global __save_history_function
    
    if __save_history_function is not None:
        # Already started
        return
    
    # noinspection PyBroadException
    try:
        import readline
    except:  # don't know, don't care, it doesn't work, carry on
        __save_history_function = lambda: None
        return
    
    history_file = os.path.join( MENV.local_data.local_folder( constants.FOLDER_SETTINGS ), "command-history.txt" )
    
    
    class __Completer:
        """
        Used by readline to manage autocompletion of the command line.
        """
        
        
        def __init__( self ):
            """
            Constructor.
            """
            self.matches = []
            self.keywords = [MENV.host.translate_name( x.name ) for x in MENV.plugins.all_plugins() if x.is_visible]
        
        
        def complete( self, text: str, state: int ) -> Optional[str]:
            """
            See readline.set_completer.
            """
            if state == 0:
                self.matches = [x for x in self.keywords if text in x]
            
            if state < 0 or state >= len( self.matches ):
                return None
            else:
                return self.matches[state]
        
        
        # noinspection PyUnusedLocal
        def show( self, substitution: str, matches: List[str], longest_match_length: int ) -> None:
            """
            See readline.set_completion_display_matches_hook.
            """
            print()
            print( constants.COL_CMD + str( len( matches ) ) + constants.COLX + " matches for " + constants.COL_CMD + substitution + constants.COLX + ":" )
            
            if len( self.matches ) > 10:
                print( "Maybe you meant something a little less ambiguous..." )
            else:
                for x in self.matches:
                    print( "Command " + constants.COL_CMD + str( x ) + constants.COLX )
    
    
    if history_file:
        if path.isfile( history_file ):
            try:
                readline.read_history_file( history_file )
            except Exception:
                warnings.warn( "Error using history file «{}». This may be a version incompatibility. History not loaded and the file will be overwritten.".format( history_file ) )
    
    readline.parse_and_bind( 'tab: complete' )
    readline.parse_and_bind( 'set show-all-if-ambiguous on' )
    completer = __Completer()
    readline.set_completer( completer.complete )
    # readline.set_completion_display_matches_hook( completer.show )
    readline.set_completer_delims( " " )
    
    
    def __write_history_file():
        if history_file:
            try:
                readline.write_history_file( history_file )
            except Exception as ex:
                raise IOError( "Failed to write the history file to «{}».".format( history_file ) ) from ex
    
    
    __save_history_function = __write_history_file


def start_cli( read_argv ) -> None:
    """
    Runs script mode (this is a bit like just executing lots of commands from the command line)
    """
    __begin_readline()
    
    host = MENV.host
    
    from intermake.hosts.console import ConsoleHost
    
    if not isinstance( host, ConsoleHost ):
        raise ValueError( "`start_cli` requires a `ConsoleHost` or `ConsoleHost`-derived host but my host is «{}».".format( repr( host ) ) )
    
    run_type = host.console_configuration.run_mode
    
    # Run the startup arguments
    queue = []
    
    if read_argv:
        for arg in sys.argv[1:]:
            queue.append( arg )
        
        if not queue:
            MENV.host = MENV.host_provider( ERunMode.CLI )
            MENV.host.run_host( RunHostArgs() )
    
    try:
        while True:
            if read_argv:
                if not queue:
                    raise UserExitError( "All arguments parsed" )
                
                x = queue.pop( 0 )
            else:
                x = __read_arg()
            
            try:
                execute_text( x )
            except KeyboardInterrupt:
                host.print_message( Back.YELLOW + Fore.RED + "-------------------------------------------------" + Style.RESET_ALL, stream = EStream.SYSTEM )
                host.print_message( Back.YELLOW + Fore.RED + "- KEYBOARD INTERRUPT - OUTPUT MAY BE INCOMPLETE -" + Style.RESET_ALL, stream = EStream.SYSTEM )
                host.print_message( Back.YELLOW + Fore.RED + "-------------------------------------------------" + Style.RESET_ALL, stream = EStream.SYSTEM )
            except Exception as ex:
                if host.console_settings.error_traceback:
                    from intermake.engine import m_print_helper
                    m_print_helper.print_traceback( ex )
                else:
                    print( Fore.RED + str( ex ) + Fore.RESET )
    
    except UserExitError as ex:
        host.print_message( "[{}]".format( ex ), stream = EStream.SYSTEM )
    finally:
        host.print_message( "Exiting {} script executor.".format( run_type ), stream = EStream.SYSTEM )
        
        if not queue:
            __save_history_function()


def __read_arg():
    print( Fore.YELLOW, end = "" )
    prompt = ">>> " + str( MENV.host.browser_path ) + ">"
    
    try:
        if file_helper.is_windows():
            print( prompt, end = "" )
            return input()
        else:
            return input( prompt )
    except EOFError:
        raise UserExitError( "End of standard input" )
    except KeyboardInterrupt:
        raise UserExitError( "Keyboard quit" )
    finally:
        print( Style.RESET_ALL, end = "" )
        sys.stdout.flush()


def execute_text( x ) -> None:
    for k, v in os.environ.items():
        x = x.replace( "$(" + k + ")", v )
    
    if x.startswith( "?" ) or x.endswith( "?" ):
        x = x.strip( "?" )
        x = x.strip()
        
        user_commands = shlex.split( x )
        cmds = ["help"]
        
        if len( user_commands ) >= 1:
            cmds += [user_commands[0]]
        
        if len( user_commands ) >= 2:
            cmds += [user_commands[-1]]
    elif x.startswith( "=" ):
        x = x.strip( "=" )
        x = x.strip()
        cmds = ["cypher", "code=" + x]
    else:
        try:
            cmds = shlex.split( x )
        except:
            print( Fore.LIGHTRED_EX + "Not processing '" + constants.COLX + constants.COL_CMD + x + constants.COLX + Fore.LIGHTRED_EX + "' because it isn't valid command string." + constants.COLX )
            return
    
    __execute_command( cmds )
