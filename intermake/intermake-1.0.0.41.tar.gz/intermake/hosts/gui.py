import sys
import threading
import traceback
from typing import Callable, Optional, cast

from PyQt5.QtCore import QThread, pyqtSignal

from intermake.engine.async_result import AsyncResult
from intermake.engine.constants import EThread
from intermake.engine.environment import MENV
from intermake.engine.mandate import ArgsKwargs, Mandate
from intermake.engine.plugin import Plugin
from intermake.engine.progress_reporter import IProgressReceiver, QueryInfo, TaskCancelledError, UpdateInfo
from intermake.hosts.base import ERunMode, PluginHost, RunHostArgs
from intermake.hosts.frontends.gui_qt.frm_maintenance import FrmMaintenance
from mhelper import Logger, SwitchError, override, string_helper, virtual, ansi_format_helper


__author__ = "Martin Rusilowicz"

_SIGLOG = Logger( "gui host signals" )


class _FnWrapper:
    """
    Wraps a function, we need to do this because QT won't let us send raw functions across threads, but we can send an object that behaves like a function.
    """
    
    
    def __init__( self, fn ) -> None:
        self.__fn = fn
    
    
    def __call__( self, *args, **kwargs ) -> Optional[object]:
        return self.__fn( *args, **kwargs )
    
    
    def __str__( self ) -> str:
        return str( self.__fn )


class BrowserInvoke:
    """
    If a plugin returns this, the host runs it in the browser.
    This should be used if the host replies `True` to `has_form`.
    """
    
    
    def __init__( self, cypher: str ) -> None:
        self.cypher = cypher


class IGuiPluginHostWindow:
    def plugin_completed( self, result: AsyncResult ) -> None:
        raise NotImplementedError( "abstract" )


class _GuiHostSettings:
    """
    :attr number_of_threads: Number of threads to use in plugins supporting multi-threading.
    :attr gui_auto_close_progress: Automatically close the progress dialogue.
    :attr gui_style: GUI style (takes any viable Qt style string) 
    """
    
    
    def __init__( self ) -> None:
        super().__init__()
        self.number_of_threads = 1
        self.gui_auto_close_progress = True
        self.gui_style = ""


class CreateWindowArgs:
    def __init__( self, can_return_to_cli: bool ):
        self.can_return_to_cli = can_return_to_cli


class _NullReceiver( IProgressReceiver ):
    def progress_update( self, info: UpdateInfo ) -> None:
        pass
    
    
    def was_cancelled( self ) -> bool:
        return False
    
    
    def question( self, query: QueryInfo ) -> Optional[object]:
        raise ValueError( "Cannot question the user when a plugin is being run in the main thread! The main thread is already being used to host the GUI." )


class GuiHost( PluginHost ):
    """
    Manages a set of asynchronous workers and their progress dialogue
    
    :attr __settings:       These settings used by the GUI which can be configured by the user through the `set` command.
    :attr __owner_window:   The main window
    :attr __beehives:       Each plugin gets its own "bee hive", which manages the threads ("busy bees") for that plugin.
    :attr thread_local:     Thread-local data store. Each thread gets its own version of this, including the main thread.
    :attr thread_local.tag_receiver:     The progress receiver for a particular thread.
    :attr thread_local.tag_mandate:      The stack of plugins called on a particular thread.
    :attr __base_mandate:   This is the mandate used at the bottom of the main thread, when no plugins are running this is what `MCMD` returns. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        super().__init__()
        self.__settings: _GuiHostSettings = None
        self.__owner_window = cast( IGuiPluginHostWindow, None )
        self.__beehives = []
        self.thread_local = threading.local()
        self.thread_local.tag_receiver = _NullReceiver()
        self.__base_mandate = Mandate( self, None, None, self.thread_local.tag_receiver, "Base" )
        self.thread_local.tag_mandate = [self.__base_mandate]
        
        threading.currentThread().name = "main_intermake_gui_thread"
    
    
    def _is_cli( self ):
        return False
    
    
    def register_thread( self, mandate: Mandate ):
        if hasattr( self.thread_local, "tag_mandate" ):
            raise ValueError( "Attempt to register a thread with the GuiHost but that thread has already been registered. This is probably an error." )
        
        self.thread_local.tag_receiver = mandate._get_receiver()
        self.thread_local.tag_mandate = [mandate]
    
    
    def __str__( self ) -> str:
        return "GuiHost(QT)"
    
    
    def translate_name( self, name: str ) -> str:
        return string_helper.capitalise_first_and_fix( name, "_-." )
    
    
    def _PLUGINHOST_get_run_mode( self ) -> ERunMode:
        return ERunMode.GUI
    
    
    @override
    def get_mandate( self ) -> Mandate:
        """
        Obtains the mandate, stored in the thread-local pool for the plugin
        This doesn't work for unmanaged plugins, they need to take the mandate as a parameter.
        :return: 
        """
        try:
            return self.thread_local.tag_mandate[-1]
        except AttributeError as ex:
            raise ValueError( "Attempt to get the mandate from a thread «{}» that is neither the main thread nor a thread running a plugin.".format( threading.currentThread().name ) ) from ex
    
    
    def get_help_message( self ) -> str:
        return """
            You are in GUI mode.
            Double-click plugins to run them.
            Try running the sample `eggs` plugin, which can be found in the `Default/Commands` folder."""
    
    
    def __is_in_plugin( self ):
        return self.thread_local.tag_mandate[0] is not self.__base_mandate
    
    
    @virtual
    def create_window( self, args: CreateWindowArgs ):
        from intermake.hosts.frontends.gui_qt.frm_main import FrmMain
        frm_main = FrmMain( args.can_return_to_cli )
        return frm_main
    
    
    @override
    def run_host( self, args: RunHostArgs ):
        """
        Helper function to start the GUI
        """
        # Unfortunate notice: If the GUI fails to initialise with a segmentation fault this is probably a bad QT
        # installation. The user will need to reinstall QT/PyQt5. TODO: Detect this scenario and inform the user.
        from intermake.engine import cli_helper
        cli_helper.print_banner( ERunMode.GUI )
        
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Start the GUI
        if self.gui_settings.gui_style:
            QApplication.setStyle( self.gui_settings.gui_style )
        
        app = QApplication( sys.argv )
        main_window = self.create_window( CreateWindowArgs( can_return_to_cli = args.can_return ) )
        self.set_window( main_window )
        main_window.show()
        
        app.exec_()
        
        return main_window.return_to_console
    
    
    def set_window( self, window: IGuiPluginHostWindow ):
        self.__owner_window = window
    
    
    @property
    def gui_settings( self ) -> _GuiHostSettings:
        if self.__settings is None:
            self.__settings = MENV.local_data.store.retrieve( "gui", _GuiHostSettings )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    @override
    def call_virtual_run( self, plugin: Plugin, args: ArgsKwargs, callback: Optional[Callable[[], None]], force_sync: bool ) -> Optional[object]:
        """
        IMPLEMENTATION
        """
        if self.__is_in_plugin() or force_sync or plugin.threading() == EThread.UNMANAGED:
            return self.__invoke_unmanaged( plugin, args, callback, force_sync )
        elif plugin.threading() == EThread.SINGLE:
            self.__invoke_threaded( plugin, args, 1, callback )
            return None
        elif plugin.threading() == EThread.MULTI:
            self.__invoke_threaded( plugin, args, self.settings.number_of_threads, callback )
            return None
        else:
            raise SwitchError( "plugin.threading( )", plugin.threading() )
    
    
    def __invoke_unmanaged( self, plugin: Plugin, args: ArgsKwargs, callback: Optional[Callable[[AsyncResult], None]], sync: bool ) -> Optional[object]:
        def f():
            self.thread_local.tag_mandate.append( Mandate( self, plugin, args, self.thread_local.tag_receiver, plugin.name ) )
            
            try:
                return plugin.call_virtual_run()
            finally:
                self.thread_local.tag_mandate.pop()
        
        
        if sync:
            return f()
        
        result = AsyncResult.construct( f, plugin.name )
        
        if callback:
            callback( result )
        else:
            self.__owner_window.plugin_completed( result )
        
        return result
    
    
    def __invoke_threaded( self, plugin: Plugin, args: ArgsKwargs, num_threads: int, callback: Optional[Callable[[], None]] ) -> None:
        self.__beehives.append( self.__BeeHive( self, self.__owner_window, plugin, args, num_threads, callback ) )
    
    
    @override
    def set_last_result( self, result ):
        super().set_last_result( result )
        self.__owner_window.plugin_completed( result )
    
    
    class __BeeHive:
        def __init__( self, host, window, plugin: Plugin, args: ArgsKwargs, num_threads: int, callback: Optional[Callable[[], None]] ):
            if window is None:
                raise ValueError( "__BeeHive expects a Window." )
            
            self._dialogue = FrmMaintenance( window, plugin.name )
            self._dialogue.show()
            
            self._host = host
            self.__callback = callback
            self.__plugin = plugin
            
            self.__bees = set()
            
            for i in range( num_threads ):
                bee = self.__BusyBee( self, plugin, args, self._dialogue, i, num_threads )
                
                bee.start()
                self.__bees.add( bee )
        
        
        def bee_finished( self, bee: "__BusyBee", result: AsyncResult ) -> None:
            """
            Called when a thread finishes (back in the main thread)
            """
            self.__bees.remove( bee )
            
            if self.__bees:
                return
            
            # Close the dialogue
            self._dialogue.worker_finished( result )
            
            # Tell the caller we are done (they only get the last result)
            
            if self.__callback:
                self.__callback( result )
            else:
                self._host.set_last_result( result )
        
        
        class __BusyBee( QThread, IProgressReceiver ):
            """
            Actual thread
            """
            __callback = pyqtSignal( _FnWrapper )
            
            
            @override  # IProgressReceiver
            def was_cancelled( self ) -> bool:
                return self.__dialogue.was_cancelled()
            
            
            @override  # IProgressReceiver
            def question( self, query: QueryInfo ) -> Optional[object]:
                raise NotImplementedError( "This feature (question user) has not been implemented in the GUI, please run in the CLI." )  # TODO!!!
            
            
            @override  # IProgressReceiver
            def progress_update( self, info ) -> None:
                self.invoke_in_main_thread( lambda: self.__dialogue.worker_update( info ) )
            
            
            def __init__( self, hive: "GuiHost.__BeeHive", plugin: Plugin, args: ArgsKwargs, dialogue, my_index, num_threads ):  # MAIN
                """
                Creates the thread object
                """
                QThread.__init__( self )
                
                self.__callback.connect( self.__invoke_returned )
                
                self.__args = args
                self.__plugin = plugin  # type: Plugin
                
                self.__dialogue = dialogue
                
                self.__result = None  # type:Optional[object]
                self.__exception = None  # type:Optional[Exception]
                self.__exception_trace = None  # type: Optional[str]
                
                self.__was_cancelled = False
                self.__hive = hive
                
                self.__mandate = Mandate( self.__hive._host, self.__plugin, self.__args, self, plugin.name, my_index, num_threads, 0.2 )
            
            
            @override  # QThread
            def run( self ) -> None:  # WORKER
                """
                QThread Implementation
                """
                
                threading.currentThread().name = "intermake_busybee_{}_hive_{}_running_{}".format( id( self ), id( self.__hive ), self.__plugin.name.replace( " ", "_" ) )
                
                try:
                    self.__hive._host.thread_local.tag_mandate = [self.__mandate]
                    self.__hive._host.thread_local.tag_receiver = self
                    true_result = self.__plugin.call_virtual_run()
                    result = AsyncResult( self.__plugin.name, true_result, None, None, self.__mandate.get_message_records() )
                except TaskCancelledError as ex:
                    result = AsyncResult( self.__plugin.name, None, ex, traceback.format_exc(), self.__mandate.get_message_records() )
                except Exception as ex:
                    result = AsyncResult( self.__plugin.name, None, ex, traceback.format_exc(), self.__mandate.get_message_records() )
                    
                    # Print a message for the debugger
                    print( "EXCEPTION IN __BusyBee.run:", file = sys.stderr )
                    print( ansi_format_helper.format_traceback( ex ), file = sys.stderr )
                
                self.invoke_in_main_thread( lambda: self.__hive.bee_finished( self, result ) )
            
            
            def invoke_in_main_thread( self, where ) -> None:  # WORKER
                """
                Calls "where" back in the main thread
                """
                where = _FnWrapper( where )
                _SIGLOG( "S __invoke_emit --> {}".format( where ) )
                self.__callback.emit( where )  # --> MAIN (via signal)
                _SIGLOG( "E __invoke_emit --> {}".format( where ) )
            
            
            @staticmethod
            def __invoke_returned( where ) -> None:  # <- MAIN (via signal)
                """
                The callback from invoke_in_main_thread - just calls "where".
                """
                _SIGLOG( "S __invoke_returned --> {}".format( where ) )
                where()
                _SIGLOG( "E __invoke_returned --> {}".format( where ) )
    
    
    @override
    def has_form( self ):
        return True
    
    
    @override
    def form( self ):
        return self.__owner_window
