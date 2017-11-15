from typing import Any, Callable, List, Optional, Tuple, TypeVar

from mhelper import MEnum
from intermake.engine import constants
from intermake.engine.async_result import AsyncResult
from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo
from mhelper.comment_helper import abstract, override, virtual
from mhelper.exception_helper import SwitchError

T=TypeVar("T")

__author__ = "Martin Rusilowicz"


class _PluginHostSettings:
    """
    :data number_of_results_to_keep: Number of results to keep in history
    :data welcome_message: Whether to display the welcome message when the host starts
    """
    
    
    def __init__( self ):
        self.number_of_results_to_keep = 10
        self.welcome_message = False


class RunHostArgs:
    """
    Arguments passed to a host when it runs.
    """
    
    
    def __init__( self, read_argv: bool = False, can_return: bool = True ):
        """
        CONSTRUCTOR
        :param read_argv:        The host should interpret the command-line arguments. Secondary hosts (i.e. anything that isn't the first `ConsoleHost`) aren't expected to receive this.
        :param can_return:      The result of the host's `run_host` method will be used to determine if the calling host should exit. Primary hosts (i.e. the first `ConsoleHost`) aren't expected to receive this.
        """
        self.read_argv = read_argv
        self.can_return = can_return


class ERunMode( MEnum ):
    """
    How the host should run. Also determines the initial configuration.
    
    :remarks: See also `create_simple_host_provider` and `create_simple_host_provider_from_class`.
              `ARG`, `CLI`, `PYI` and `PYS` all run under `ConsoleHost` by default, whilst `GUI` runs under the Qt `GuiHost`.
    
    :data ARG: Parses command line arguments
    :data CLI: Console-based host with a command-line-interactive frontend.
    :data PYI: Console-based host with a Python-interactive frontend.
    :data PYS: Console-based host without a frontend. For your own Python scripts.
    :data GUI: Graphical host with a graphical frontend.
    """
    ARG = 0
    CLI = 1
    PYI = 2
    PYS = 3
    GUI = 4


@abstract
class PluginHost:
    """
    All plugins run under a `PluginHost`, this is it.

    Operation logic follows:

        (TODO)

    Only `virtual_run` need be implemented by the derived class.
    """
    _pluginHostCount = 0
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        PluginHost._pluginHostCount += 1
        self.__settings = None  # type: _PluginHostSettings
        self._index = PluginHost._pluginHostCount
        self.last_results = [ ]  # type: List[Tuple[int, AsyncResult]]
        self.__num_results = 0
        self.last_result = AsyncResult( None, None, None, None, None )
        self.last_error = AsyncResult( None, None, None, None, None )
    
    @virtual
    def get_help_message( self ):
        """
        Provides the help the user gets when they type `basic_help`.
        """
        return """You are running in a {} host and I can't give you any help because the creator of this host hasn't provided a `get_help_message`.
        Please see `readme.md` in the application directory for more information.""".format( type( self ).__name__ )
    
    
    @abstract
    def _PLUGINHOST_get_run_mode( self ) -> ERunMode:
        """
        Gets the run-mode hint.
        """
        raise NotImplementedError( "abstract" )
    
    
    @property
    def run_mode( self ):
        return self._PLUGINHOST_get_run_mode
    
    
    @property
    def host_settings( self ) -> _PluginHostSettings:
        """
        Obtains the settings used to control the base host class.
        :return:    Settings. 
        """
        if self.__settings is None:
            from intermake.engine.environment import MENV
            self.__settings = MENV.local_data.store.retrieve( "host", _PluginHostSettings )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    @virtual
    def run_host( self, args: RunHostArgs ):
        """
        Runs the host's main loop, if it has one.
        :param args:    Arguments 
        :return:        `True` to return to the previous host, `False` to tell the previous host to exit too. 
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def substitute_text( self, text ):
        """
        Formats help text for the current host.
        
        The base implementation replaces $(XXX) from the set of constants. 
        
        Concrete hosts may override this further.
        
        :param text:    Input text 
        :return:        Text to display 
        """
        from intermake.engine.environment import MENV
        
        text = text.replace( "$(APPNAME)", MENV.abv_name )
        
        for k, v in MENV.constants.items():
            text = text.replace( "$(" + k + ")", v )  # TODO: Inefficient
        
        return text
    
    
    @abstract
    def _get_mandate( self ):
        """
        Obtains the mandate for the plugin being run (on the current thread).
        Note: To get the mandate externally, use the `current_mandate()` function.
        
        This function must be overridden by the concrete host.
        :rtype: Mandate 
        """
        raise NotImplementedError( "abstract" )
    
    
    @property
    def console_width( self ):
        """
        Some plugins want to know the width of the screen for text-display purposes.
        This is how they get that.
        
        This calls the `_get_console_width` virtual function.
         
        :return: Width of text, in characters. 
        """
        return min(180, self._get_console_width())
    
    @property
    def console_width_unsafe( self ):
        """
        `console_width`, without clamping. This may be a large value - use only for wrapping, not for padding!
        """
        return self._get_console_width()
    
    
    @virtual
    def _get_console_width( self ):
        """
        When obtaining the width of the screen this function is called.
        The base implementation suggests no wrapping (an arbitrary large value).
        The derived class may suggest more appropriate text-wrapping limit.
        :return: 
        """
        return 1000
    
    
    @abstract
    def call_virtual_run( self, plugin, args, callback, sync ) -> Optional[ object ]:
        """
        Called for implementation-specific running of a plugin.
        This process exists so the derived hosts execute the plugin in the thread or method of their choice.

        The implementing class should respond by:
            1. Ensuring `PluginHost._get_mandate` returns an appropriate value when called from within `Plugin.call_virtual_run`.
            2. Calling `Plugin.call_virtual_run` on the plugin object.
         
        :param callback:
        :param args:
        :param plugin:
        :param sync:
         
        :type callback:    Optional[Callable[[AsyncResult],None]]
        :type args:        ArgsKwargs
        :type plugin:      Plugin
        :type sync:        bool
        """
        raise NotImplementedError( "Abstract" )
    
    
    @virtual
    def has_form( self ):
        """
        Returns if it is okay to call `form`. 
        """
        return False
    
    
    @virtual
    def form( self ):
        """
        Gets the form associated with the host
        Meaningless for a non-GUI host
        """
        raise ValueError( "This plugin must be run under a GUI." )
    
    
    def translate_name( self, name: str ) -> str:
        """
        Given the `name` of an object, translates it into something more friendly to the user.
        """
        raise NotImplementedError( "Abstract" )
    
    
    def set_last_result( self, result: AsyncResult ):
        """
        :param result:
         
        :type result: AsyncResult
        :rtype: None
        """
        self.__num_results += 1
        result.title = str( self.__num_results ) + ". " + result.title
        
        self.last_results.append( (self.__num_results, result) )
        
        while len( self.last_results ) > self.host_settings.number_of_results_to_keep:
            self.last_results.pop( 0 )
        
        if result.success:
            if result.result is not None:
                self.last_result = result
        else:
            if result.exception is not None:
                self.last_error = result


class _AsyncResultAsVisualisable( IVisualisable ):
    """
    Wraps an individual result to an `IVisualisable` so the user can explore it. 
    """
    
    
    def __init__( self, name, data: AsyncResult, comment ):
        """
        :param name:    Name of the result (name of the result, e.g. last, error, 1, 2, 3...)
        :param data:    The actual AsyncResult 
        :param comment: Comment on the result (where it came from, e.g. my_super_plugin)
        """
        self.name = name
        self.data = data
        self.comment = comment
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.comment or self.data.title,
                       type_name = "Result",
                       value = str( self.data ),
                       colour = EColour.RED if self.data.is_error else EColour.YELLOW if self.data.result is None else EColour.BLUE,
                       icon = resources.failure if self.data.is_error else resources.success if self.data.result is None else resources.successplus,
                       extra = { "result"   : self.data.result,
                                 "exception": self.data.exception,
                                 "traceback": self.data.traceback,
                                 "messages" : self.data.messages } )


class ResultsExplorer( IVisualisable ):
    """
    The `ResultsExplorer` class is used to explore results from the execution of previous
    plugins, wrapping the set of results into an `IVisualisable` object. 
    """
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        from intermake.engine.environment import MENV
        host = MENV.host
        
        return UiInfo( name = constants.EXPLORER_KEY_RESULTS,
                       comment = "Holds the last result",
                       type_name = constants.VIRTUAL_FOLDER,
                       value = self.__visualisable_info_value(),
                       colour = EColour.YELLOW,
                       icon = resources.folder,
                       extra = { "last"   : host.last_result,
                                 "error"  : host.last_error,
                                 "history": host.last_results } )
    
    @override
    def __str__( self ):
        return constants.EXPLORER_KEY_RESULTS
    
    
    @staticmethod
    def __visualisable_info_value():
        """
        Value property of `visualisable_info`.
        """
        from intermake.engine.environment import MENV
        host = MENV.host
        
        if not host.last_results:
            return "(empty)"
        
        _, last_result = host.last_results[ -1 ]
        
        if last_result.success:
            if last_result.result is not None:
                return "Data: {}".format( last_result.title )
            else:
                return "Success: {}".format( last_result.title )
        else:
            return "Error: {}".format( last_result.title )


DHostProvider = Callable[ [ ], PluginHost ]
"""
Callable that provides a plugin host.
"""

DMultiHostProvider = Callable[ [ ERunMode ], PluginHost ]
"""
Callable that, given an `ERunMode`, provides a plugin host.
"""


def create_simple_host_provider( command_arguments: DHostProvider, command_interactive: DHostProvider, python_interactive: DHostProvider, python_script: DHostProvider, gui: DHostProvider ) -> DMultiHostProvider:
    def ___fn( mode: ERunMode ) -> PluginHost:
        if mode == ERunMode.ARG:
            return command_arguments()
        elif mode == ERunMode.CLI:
            return command_interactive()
        elif mode == ERunMode.PYI:
            return python_interactive()
        elif mode == ERunMode.PYS:
            return python_script()
        elif mode == ERunMode.GUI:
            return gui()
        else:
            raise SwitchError( "mode", mode )
    
    
    return ___fn


def create_simple_host_provider_from_class( console_host_class: Any, gui_host_class: DHostProvider ) -> DMultiHostProvider:
    def ___fn( mode: ERunMode ) -> PluginHost:
        if mode == ERunMode.ARG:
            return console_host_class.get_default( mode )
        elif mode == ERunMode.CLI:
            return console_host_class.get_default( mode )
        elif mode == ERunMode.PYI:
            return console_host_class.get_default( mode )
        elif mode == ERunMode.PYS:
            return console_host_class.get_default( mode )
        elif mode == ERunMode.GUI:
            return gui_host_class()
        else:
            raise SwitchError( "mode", mode )
    
    
    return ___fn
