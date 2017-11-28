import shutil
import sys
import time
from os import system
from typing import Callable, List, Optional, TypeVar

from intermake.engine import cli_helper, constants, m_print_helper
from intermake.engine.async_result import AsyncResult
from intermake.engine.constants import EDisplay, EStream, EThread
from intermake.engine.environment import MENV
from intermake.engine.mandate import Mandate
from intermake.engine.plugin import ArgsKwargs, Plugin
from intermake.engine.progress_reporter import IProgressReceiver, QueryInfo, UpdateInfo
from intermake.engine.theme import Theme
from intermake.hosts.base import ERunMode, PluginHost, RunHostArgs
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo
from intermake.visualisables.visualisable_operations import PathToVisualisable
from mhelper import MEnum, exception_helper, file_helper, string_helper
from mhelper.comment_helper import override
from mhelper.exception_helper import SwitchError
#
# CONSTANTS
#
from mhelper.special_types import NOT_PROVIDED
from mhelper.string_helper import FindError


# Characters
_CHAR_PROGRESS_SIDE_LEFT = Theme.PROGRESS_COLOUR_PROGRESS_SIDE + "▐"
_CHAR_PROGRESS_SIDE_RIGHT = Theme.PROGRESS_COLOUR_PROGRESS_SIDE + "▌"
_CHAR_PROGRESS_SPACE_LEFT = " "
_CHAR_PROGRESS_SPACE_RIGHT = " "
_CHAR_PROGRESS_POINT = "▌"
_CHAR_PROGRESS_POINT_BOUNCY = "•••"

T = TypeVar( "T" )


class EConsoleReport( MEnum ):
    """
    Progress report types.
    
    :data SILENT: No reports
    :data ANSIART: Draw graphical loading
    :data SIMPLE: Literal dump of progress reports
    :data MESSAGES: Only display messages, not generic progress updates
    """
    SILENT = 0
    ANSIART = 1
    SIMPLE = 2
    MESSAGES = 3


class UserExitError( BaseException ):
    """
    Used as a special error to indicate the user wishes to exit. This is always raised past the usual `ConsoleHost` error
    catching, allowing termination of the front-end via the front-end error handler.
    """
    pass


class _ConsoleHostSettings:
    """
    :data console_width_override : Width of console for display. If this is zero (the default) the system is queried.
    :data clear_screen           : Clear screen between command executions
    :data force_echo             : Always echo the commands
    :data error_traceback        : Print error traceback diagnostics
    """
    
    
    def __init__( self ) -> None:
        self.console_width_override: int = 0
        self.clear_screen: bool = False
        self.force_echo: bool = False
        self.error_traceback: bool = False


class ConsoleHostConfiguration:
    """
    :data force_error_traceback: Always print the error traceback, even if the user turns it off
    :data clear_screen         : Clear screen between commands
    :data force_echo           : Echo commands
    :data report               : Reporting mode
    :data use_dot              : Use `.` instead of `_`
    :data keep_results         : Number of results to keep in history
    :data cluster_index        : Index for compute clusters
    :data cluster_count        : Count for compute clusters
    """
    
    
    def __init__( self, run_mode: ERunMode ):
        if run_mode not in (ERunMode.ARG, ERunMode.CLI, ERunMode.PYI, ERunMode.PYS):
            raise SwitchError( "run_mode", run_mode, details = "This run-mode is not supported by ConsoleHost. Did you mean to use a different host?" )
        
        self.run_mode = run_mode
        self.report = EConsoleReport.ANSIART
        self.use_dot = bool( run_mode in (ERunMode.ARG, ERunMode.CLI) )
        self.cluster_index = 0
        self.cluster_count = 1
        self.force_error_traceback = run_mode == ERunMode.ARG
    
    
    def __str__( self ) -> str:
        return "ConsoleHost({})".format( self.run_mode )


class ConsoleHost( PluginHost, IProgressReceiver ):  # this host is always single-threaded so it acts as its own progress receiver
    """
    Hosts plugins in CLI mode
    """
    
    
    def __str__( self ) -> str:
        return str( self.console_configuration )
    
    
    @classmethod
    def get_default( cls, run_mode: ERunMode ):
        return cls( ConsoleHostConfiguration( run_mode ) )
    
    
    def _PLUGINHOST_get_run_mode( self ) -> ERunMode:
        return self.console_configuration.run_mode
    
    
    def _get_console_width( self ) -> int:
        # Unpickling settings can cause errors, when these errors get printed, they loop back here, hence we avoid the loop by not forcing an unpickle of the settings at this stage
        if self.__settings is not None:
            if self.__settings.console_width_override > 0:
                return self.__settings.console_width_override
        
        return max( 10, shutil.get_terminal_size()[0] - 1 )
    
    
    def translate_name( self, name: str ) -> str:
        return self.translate_name_mode( name, self.__configuration.use_dot )
    
    
    @staticmethod
    def translate_name_mode( name: str, use_dot: bool ):
        char = "." if use_dot else "_"
        text = str( name )
        
        for x in " _-.()":
            text = text.replace( x, char )
        
        for x in "\"'":
            text = text.replace( x, "" )
        
        charchar = char + char
        
        while charchar in text:
            text = text.replace( charchar, char )
        
        text = text.lower()
        
        return text
    
    
    def __init__( self, config: ConsoleHostConfiguration ):
        """
        CONSTRUCTOR
        See the `Core.initialise` function for parameter descriptions.
        """
        super().__init__()
        self.__configuration = config
        self.__settings = None
        self.__pulse = False
        self.__last_message_id = None  # type: Optional[List[int]]
        self.__last_info_depth = None
        self.__last_info_thread_index = None
        self.__browser_path = None
        self.__mandates = []
        self.__last_stream = None
        self.__bouncy_current = 0
        self.__bouncy_delta = 1
    
    
    @override
    def run_host( self, args: RunHostArgs ):
        """
        Runs the host's main loop.
        """
        run_mode = self.console_configuration.run_mode
        
        if self.console_settings.clear_screen:
            from intermake.plugins.common_commands import cls
            cls()
        
        cli_helper.print_banner( run_mode )
        
        # if cli_helper.print_banner( run_mode ):
        #     from intermake.plugins import console_explorer
        #     self.print_message( console_explorer.resultsexplorer_ls(), stream = EStream.INFORMATION )
        
        if run_mode == ERunMode.ARG:
            from intermake.hosts.frontends.command_line import start_cli
            start_cli( args.read_argv )
        elif run_mode == ERunMode.CLI:
            from intermake.hosts.frontends.command_line import start_cli
            start_cli( False )
        elif run_mode == ERunMode.PYI:
            import code
            code.interact( local = MENV.plugins.to_dictionary() )
        elif run_mode == ERunMode.PYS:
            # This host does not "run"
            pass
        else:
            raise SwitchError( "run_mode", run_mode )
    
    
    def get_help_message( self ) -> str:
        if self.console_configuration.run_mode == ERunMode.ARG:
            return """
            Welcome to $(APPNAME). You are in command line arguments (ARG) mode.
            
            Usage:
                `$(APPNAME) "commands"`
                
            To see the list of commands type:

                `$(APPNAME) cmdlist`
                
            Or to run the `eggs` command:
            
                `$(APPNAME) eggs`

            You can use `?` to get help on a command:

                `$(APPNAME) eggs?`

            See that "eggs" takes two arguments, "name" and "good".
            
            You can specify the arguments after the command. We need quotes in BASH or CMD.EXE because our command now contains spaces:

                `$(APPNAME) "eggs Humpty True"`

            You can also name the arguments:

                `$(APPNAME) "eggs good=True"`

            You can also use `?` to get help on the last argument:

                `$(APPNAME) "eggs name?"`

            Specify `+` and `-` to quickly set boolean arguments:

                `$(APPNAME) "eggs +good"`

            You should use more quotes to pass parameters with spaces:

                `$(APPNAME) "eggs 'Humpty Dumpty'"`
                
            For the list of commands type:
            
                `$(APPNAME) cmdlist`
                
            To start the UI:
            
                `$(APPNAME) ui cli`
                
            Use : to pass multiple commands
            
                `$(APPNAME) cmdlist : ui cli`

            If you don't specify any commands, the CLI UI will start automatically.
            """
        elif self.console_configuration.run_mode == ERunMode.CLI:
            return """
            Welcome to $(APPNAME). You are in command line interactive (CLI) mode.
            
            To see the list of commands type:
            
                `cmdlist`

            To run a command just type it, e.g. for the "eggs" command:

                `eggs`

            You can use `?` to get help on a command:

                `eggs?`

            See that "eggs" takes two arguments, "name" and "good".
            
            You can specify the arguments after the command:

                `eggs Humpty True`

            You can also name the arguments:

                `eggs good=True`

            You can also use `?` to get help on the last argument:

                `eggs name?`

            Specify `+` and `-` to quickly set boolean arguments:

                `eggs +good`

            You should use quotes to pass parameters with spaces:

                `eggs "Humpty Dumpty"`
            """
        elif self.console_configuration.run_mode == ERunMode.PYI:
            return """
            Welcome to $(APPNAME). You are in Python interactive (PYI) mode.
            
            Run the `cmdlist` function to get the list of $(APPNAME) features.
            
                `cmdlist()`

            Run $(APPNAME) commands like you would in Python, for instance to run the `eggs` command:

                `eggs()`

            You can use .help() for help:

                `eggs.help()`

            You can see that `eggs` takes two arguments, `name` and `good`.
            
            Specify arguments like in Python:

                `eggs("Humpty", True)`

            Or you can name them:

                `eggs(name = "Humpty", good = True)`
            """
        elif self.console_configuration.run_mode == ERunMode.PYS:
            return """
            Welcome to $(APPNAME). You are in Python scripting (PYS) mode.
            
            The `cmdlist` command provides the complete list of features:

                `from  $(APPNAME) import commands`
                `commands.cmdlist()`

            You can call commands directly, for instance to run the "eggs" command:

                `from  $(APPNAME) import commands`
                `commands.eggs()`

            This mode avoids polluting the global namespace.
            Usage is otherwise the same as PYI mode.
            """
        else:
            return super().get_help_message()
    
    
    @property
    def console_configuration( self ) -> ConsoleHostConfiguration:
        return self.__configuration
    
    
    @property
    def console_settings( self ) -> _ConsoleHostSettings:
        if self.__settings is None:
            self.__settings = MENV.local_data.store.retrieve( "console", _ConsoleHostSettings )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    @property
    def browser_path( self ) -> PathToVisualisable:
        if self.__browser_path is None:
            root = MENV.root
            
            if root is not None:
                self.__browser_path = PathToVisualisable.root_path( root )
            else:
                self.__browser_path = PathToVisualisable.root_path( _NullRoot() )
        
        return self.__browser_path
    
    
    @browser_path.setter
    def browser_path( self, value ) -> None:
        self.__browser_path = value
    
    
    @override
    def call_virtual_run( self, plugin: Plugin,
                          args: ArgsKwargs,
                          callback: Optional[Callable[[AsyncResult], None]],
                          sync: bool ) -> Optional[object]:
        """
        OVERRIDE
        CLI mode:
        * Invokes the plugin in the current thread, this means it can return the result verbatim as well.
        * Raises exceptions in case of error, since everything is verbatim
        """
        host = MENV.host
        
        if not sync:
            if self.console_settings.clear_screen:
                if file_helper.is_windows():
                    system( "cls" )
                else:
                    system( "clear" )
                
                echo = True
            elif self.console_settings.force_echo:
                echo = True
            else:
                echo = False
            
            if echo:
                msg = [Theme.COMMAND_NAME + host.translate_name( plugin.name ) + Theme.RESET]
                
                for index, arg in enumerate( args.args ):
                    if index >= len( plugin.args ):
                        raise ValueError( "Cannot invoke plugin «{}» with more arguments ({}: {}) than the plugin takes ({}: {}).".format( plugin, len( args.args ), args.args, len( plugin.args ), plugin.args ) )
                    
                    name = plugin.args[index].name
                    arg = Theme.VALUE + str( arg ) + Theme.RESET
                    if " " in arg or "\"" in arg:
                        msg.append( Theme.ARGUMENT_NAME + " \"" + name + "=" + arg + "\"" + Theme.RESET )
                    else:
                        msg.append( Theme.ARGUMENT_NAME + " " + name + "=" + arg + Theme.RESET )
                
                for name, arg in args.kwargs.items():
                    name = Theme.ARGUMENT_NAME + name + Theme.RESET
                    arg = Theme.VALUE + str( arg ) + Theme.RESET
                    if " " in arg or "\"" in arg:
                        msg.append( Theme.ARGUMENT_NAME + " \"" + name + "=" + arg + "\"" + Theme.RESET )
                    else:
                        msg.append( Theme.ARGUMENT_NAME + " " + name + "=" + arg + Theme.RESET )
                
                msg.append( Theme.RESET )
                
                self.print_message( "".join( msg ), EStream.ECHO )
        
        mandate = Mandate( host, plugin, args, self, plugin.name, self.__configuration.cluster_index, self.__configuration.cluster_count, 0.1 )
        
        try:
            if self.__configuration.cluster_count != 1:
                if plugin.threading() != EThread.UNMANAGED:
                    mandate.warning( "Multiple processors have been specified but the «{0}» plugin does not support a divided workload.".format( plugin.name ) )
            
            self.__mandates.append( mandate )
            
            try:
                result = plugin.call_virtual_run()
            finally:
                self.end_progress_bar()
                self.__mandates.pop( -1 )
            
            async_result = AsyncResult( plugin.name, result, None, None, mandate.get_message_records() )
        except BaseException as ex:
            async_result = AsyncResult( plugin.name, None, ex, exception_helper.full_traceback(), mandate.get_message_records() )
            self.__send_result( callback, async_result )
            raise
        
        self.__send_result( callback, async_result )
        return async_result.result
    
    
    def __send_result( self, callback: Callable[[AsyncResult], None], async_result: AsyncResult ) -> None:
        if callback:
            callback( async_result )
        
        self.set_last_result( async_result )
    
    
    def end_progress_bar( self ) -> None:
        """
        If the console cursor is still at the end of a progress bar, be done with it and finish the line.
        """
        if self.__last_message_id is not None:
            sys.stdout.write( "⏎\n" )
            sys.stdout.flush()
            self.__last_message_id = None
        else:
            sys.stdout.flush()
    
    
    def print_message( self, message: str, stream: EStream = EStream.PROGRESS ):
        """
        Calling the inbuilt `print` won't place the newline at the end of any progress bar, so we use this to print things in CLI mode.
        This is for internal use only. Plugins should use `MCMD.print` to allow printing in other hosts (e.g. GUI) also.
        """
        if self is not None:
            self.end_progress_bar()
        
        prefix, prefix_s, suffix = self.__get_message_style( stream )
        lines = str( message ).split( "\n" )
        
        if stream == EStream.WARNING and len( lines ) == 1 and len( lines[0] ) <= (self.console_width - 4):
            for n in range( 0, 4 ):
                print( constants.INFOLINE_WARNING + Theme.WARNING + lines[0] + suffix, file = sys.stderr, end = "\r" )
                sys.stderr.flush()
                time.sleep( 0.05 )
                print( prefix + lines[0] + suffix, file = sys.stderr, end = "\r" )
                sys.stderr.flush()
                time.sleep( 0.05 )
            
            print( "", file = sys.stderr )
        else:
            for index, line in enumerate( lines ):
                if index == 0 and (self is None or self.__last_stream != stream):
                    print( prefix + line + suffix, file = sys.stderr )
                else:
                    print( prefix_s + line + suffix, file = sys.stderr )
        
        if self is not None:
            self.__last_stream = stream
        
        sys.stderr.flush()
    
    
    def __get_message_style( self, stream: EStream ):
        if stream == EStream.INFORMATION:
            prefix = constants.INFOLINE_INFORMATION
            prefix_s = constants.INFOLINE_INFORMATION_CONTINUED
            suffix = ""
        elif stream == EStream.PROGRESS:
            prefix = constants.INFOLINE_MESSAGE
            prefix_s = constants.INFOLINE_MESSAGE_CONTINUED
            suffix = ""
        elif stream == EStream.WARNING:
            prefix = constants.INFOLINE_WARNING + Theme.WARNING
            prefix_s = constants.INFOLINE_WARNING_CONTINUED + Theme.WARNING
            suffix = Theme.RESET
        elif stream == EStream.ECHO:
            prefix = constants.INFOLINE_ECHO
            prefix_s = constants.INFOLINE_ECHO_CONTINUED
            suffix = ""
        elif stream == EStream.SYSTEM:
            prefix = constants.INFOLINE_SYSTEM
            prefix_s = constants.INFOLINE_SYSTEM_CONTINUED
            suffix = ""
        else:
            raise SwitchError( "stream", stream )
        return prefix, prefix_s, suffix
    
    
    @override  # IProgressReceiver
    def question( self, query: QueryInfo ) -> object:
        """
        Because it's single threaded, the CLI can just ask the question in the console.
        """
        self.end_progress_bar()
        return ask_cli_question( query )
    
    
    @override  # IProgressReceiver
    def progress_update( self, info: UpdateInfo ):
        """
        Progress updates in the CLI get printed direct to the console.
        """
        depth = len( info.depth )
        
        # Don't draw the title card progress indicator
        if depth == 1 and info.message is None:
            return
        
        if self.__configuration.report == EConsoleReport.SILENT:
            return
        elif self.__configuration.report == EConsoleReport.SIMPLE:
            self.__draw_progress_bar_simple( info )
        elif self.__configuration.report == EConsoleReport.ANSIART:
            self.__draw_progress_bar( info )
        elif self.__configuration.report == EConsoleReport.MESSAGES and info.message is not None:
            self.print_message( info.message, stream = info.stream )
    
    
    def __draw_progress_bar_simple( self, info: UpdateInfo ):
        depth = len( info.depth )
        
        if info.message is not None:
            self.print_message( info.message, stream = info.stream )  # to std.out
        else:
            indent = constants.INFOLINE_PROGRESS + ("-" * depth if depth > 0 else "")
            indent_s = constants.INFOLINE_PROGRESS_CONTINUED + ("-" * depth if depth > 0 else "")
            
            print( indent + " PROGRESS: text    = {}".format( Theme.PROGRESS_SIMPLE + info.text + Theme.RESET ), file = sys.stderr )
            
            # if info.depth != self.__last_info_depth:
            #    print( indent_s + "         : depth   = {} ({})".format( ", ".join( str( x ) for x in info.depth ), depth ) )
            #    self.__last_info_depth = info.depth
            
            if info.thread_index != self.__last_info_thread_index:
                print( indent_s + "         : thread  = {} / {}".format( info.thread_index, info.num_threads ), file = sys.stderr )
                self.__last_info_thread_index = info.thread_index
            
            if info.value > 0:
                print( indent_s + "         : value   = {} / {}".format( info.value, info.max ), file = sys.stderr )
            
            if info.value_string:
                print( indent_s + "         : value$  = {}".format( info.value_string ), file = sys.stderr )
            
            print( indent_s + "         : passed  = {}".format( string_helper.time_to_string_short( info.total_time ) ), file = sys.stderr )
            
            remain_text = info.format_time( EDisplay.TIME_REMAINING_SHORT )
            
            if remain_text:
                print( indent_s + "         : remain  = {}".format( remain_text ), file = sys.stderr )
        
        sys.stdout.flush()
    
    
    def __draw_progress_bar( self, info: UpdateInfo ):
        if info.message is not None:
            self.print_message( info.message, stream = info.stream )  # to std.out
            return
        
        #
        # Where to draw
        #
        
        this_message_id = [info.uid] + [info.thread_index]
        this_message_id.extend( info.depth )
        
        if this_message_id == self.__last_message_id or self.__last_message_id is None:
            # Same source as last message - overwrite existing line
            print( "\r", end = "", file = sys.stderr )
        elif this_message_id == self.__last_message_id[:-1]:
            # Up one level from last message - don't print anything unless there is extra information
            if not info.value and not info.value_string:
                return
        else:
            # Down one level from last message - start a new line
            self.end_progress_bar()
        
        self.__last_message_id = this_message_id
        
        #
        # What to draw
        #
        WIDTH_SEPARATOR = 3
        WIDTH_THREAD = 2
        WIDTH_TIME = 10
        WIDTH_TOTAL = self.console_width - (WIDTH_SEPARATOR * 4) - WIDTH_THREAD - WIDTH_TIME
        WIDTH_TITLE = int( 0.5 * WIDTH_TOTAL )
        WIDTH_CURRENT = int( 0.25 * WIDTH_TOTAL )
        WIDTH_BAR = int( 0.25 * WIDTH_TOTAL )
        WIDTH_BAR_BOUNCY = WIDTH_BAR - 3
        
        # THREAD COLUMN
        if info.num_threads != 1:
            cell_thread = m_print_helper.ljust( str( info.thread_index ), " ", WIDTH_THREAD ) + Theme.PROGRESS_CHAR_COLUMN_SEPARATOR
        else:
            cell_thread = ""
        
        # TITLE COLUMN
        col_title_text = "▸" * (len( info.depth ) - 1) + info.text
        cell_title = Theme.PROGRESS_COLOUR_TITLE_COLUMN + m_print_helper.ljust( col_title_text, " ", WIDTH_TITLE ) + " "
        
        # CURRENT COLUMN
        cell_progress = Theme.PROGRESS_COLOUR_CURRENT_COLUMN + " " + m_print_helper.ljust( info.format_progress(), " ", WIDTH_CURRENT ) + " "
        
        _colour_progress_left = Theme.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY[len( info.depth ) % len( Theme.PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY )]
        
        # BAR COLUMN
        if info.max > 0:
            val = int( (info.value / info.max) * WIDTH_BAR )
            
            if 0 <= val < WIDTH_BAR:
                # Normal bar
                cell_bar = (Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                            + _CHAR_PROGRESS_SIDE_LEFT
                            + _colour_progress_left
                            + m_print_helper.ljust( info.value, _CHAR_PROGRESS_SPACE_LEFT, val )
                            + Theme.PROGRESS_COLOUR_PROGRESS_POINT
                            + _CHAR_PROGRESS_POINT
                            + Theme.PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT
                            + m_print_helper.rjust( info.max - info.value, _CHAR_PROGRESS_SPACE_RIGHT, (WIDTH_BAR - val) )
                            + Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                            + _CHAR_PROGRESS_SIDE_RIGHT
                            + Theme.RESET)
            elif val == WIDTH_BAR:
                # Full "done" bar
                cell_bar = (Theme.PROGRESS_COLOUR_CURRENT_COLUMN + ("▒" * (WIDTH_BAR + 2)))
            else:
                # Overfull bar
                val = WIDTH_BAR // 2
                cell_bar = (Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                            + _CHAR_PROGRESS_SIDE_LEFT
                            + _colour_progress_left
                            + m_print_helper.ljust( "?", "?", val )
                            + Theme.PROGRESS_COLOUR_PROGRESS_POINT
                            + "?"
                            + Theme.PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT
                            + m_print_helper.rjust( "?", "?", (WIDTH_BAR - val) )
                            + Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                            + _CHAR_PROGRESS_SIDE_RIGHT
                            + Theme.RESET)
        else:
            # Bouncy bar
            cell_bar = (Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                        + _CHAR_PROGRESS_SIDE_LEFT
                        + Theme.PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT
                        + (_CHAR_PROGRESS_SPACE_LEFT * self.__bouncy_current)
                        + Theme.PROGRESS_COLOUR_PROGRESS_POINT
                        + _CHAR_PROGRESS_POINT_BOUNCY
                        + Theme.PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT
                        + (_CHAR_PROGRESS_SPACE_LEFT * (WIDTH_BAR_BOUNCY - self.__bouncy_current))
                        + Theme.PROGRESS_COLOUR_PROGRESS_SIDE
                        + _CHAR_PROGRESS_SIDE_RIGHT
                        + Theme.RESET)
            
            self.__bouncy_current += self.__bouncy_delta
            
            if self.__bouncy_current == WIDTH_BAR_BOUNCY or self.__bouncy_current == 0:
                self.__bouncy_delta = -self.__bouncy_delta
                
                # TIME COLUMN
        self.__pulse = not self.__pulse
        
        if 0 < info.max != info.value:
            time_remaining = info.estimate_time()[-1]
            time_remaining_prefix = "-"
        else:
            time_remaining = info.total_time  # time elapsed
            time_remaining_prefix = "+"
        
        time_remaining_text = " " + time_remaining_prefix + string_helper.time_to_string_short( time_remaining, ":" if self.__pulse else " " )
        cell_time = Theme.PROGRESS_COLOUR_TIME_COLUMN + m_print_helper.ljust( time_remaining_text, " ", WIDTH_TIME ) + Theme.RESET
        
        # FORMAT EVERYTHING
        text = constants.INFOLINE_PROGRESS + cell_thread + cell_title + Theme.PROGRESS_CHAR_COLUMN_SEPARATOR + cell_progress + Theme.PROGRESS_CHAR_COLUMN_SEPARATOR + cell_bar + Theme.PROGRESS_CHAR_COLUMN_SEPARATOR + cell_time + Theme.RESET + "  "
        
        # PRINT MESSAGE
        print( text, end = "", file = sys.stderr )
        sys.stderr.flush()
    
    
    @override  # IProgressReceiver
    def was_cancelled( self ) -> bool:
        """
        OVERRIDE
        Because it operates in the main thread, progress in the CLI cannot be cancelled externally.
        (However, the user can just press CTRL+C to force an error at any point, we already pick this up and handle it accordingly elsewhere.)
        """
        return False
    
    
    @override
    def get_mandate( self ) -> Mandate:
        return self.__mandates[-1] if self.__mandates else self.__system_mandate()
    
    
    def __system_mandate( self ) -> Mandate:
        return Mandate( self, None, None, self, "System", 0, 1, 0.1 )


def ask_cli_question( query: QueryInfo ):
    """
    Asks a question in the CLI.
    :param query: The query 
    :return: Selected option from query.options. 
    """
    prefix = Theme.QUERY_PREFIX + "QUERY<" + Theme.RESET + " "
    message = string_helper.prefix_lines( str( query.message ), prefix + Theme.QUERY_MESSAGE, Theme.RESET )
    print( message, file = sys.stderr )
    
    
    def ___namer( x ) -> str:
        if x is True:
            return "yes"
        elif x is False:
            return "no"
        else:
            return MENV.host.translate_name( str( x ) )
    
    message = ""
    
    for i, x in enumerate(query.options):
        if i != 0:
            message += (Theme.QUERY_BORDER + "|" + Theme.RESET)
        
        message += Theme.QUERY_OPTION + ___namer( x ) + Theme.RESET
    
        if x == query.default:
            message += "*"
            
    print( prefix + message, file = sys.stderr )
    
    while True:
        print( Theme.QUERY_PROMPT, end = "", file = sys.stderr )
        the_input = input( "QUERY> " ).lower()
        
        if not the_input:
            if query.default is not NOT_PROVIDED:
                print( Theme.RESET, end = "", file = sys.stderr )
                return query.default
        
        try:
            if len( query.options ) == 1 and query.options[0] == "*":
                return the_input
            
            result = string_helper.find( source = query.options,
                                         search = the_input,
                                         namer = ___namer,
                                         detail = "option" )
            
            print( Theme.RESET, end = "", file = sys.stderr )
            return result
        except FindError:
            print( Theme.ERROR + "Invalid option, try again." + Theme.RESET, file = sys.stderr )
            continue


class _NullRoot( IVisualisable ):
    def visualisable_info( self ) -> UiInfo:
        from intermake.hosts.frontends.gui_qt.designer import resources
        
        return UiInfo( name = MENV.abv_name, comment = "", type_name = MENV.name, value = "", colour = EColour.YELLOW, icon = resources.folder )
