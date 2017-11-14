from typing import Optional, Tuple, Dict, Sequence, Iterable, TypeVar, Union, IO

from intermake.engine.constants import EStream
from intermake.engine.plugin_arguments import PluginArgValueCollection, ArgsKwargs, PluginArg, HFunctionParameterType
from intermake.engine.progress_reporter import ProgressReporter, ActionHandler, TText
from intermake.hosts.base import PluginHost


T = TypeVar( "T" )

TIterable = Union[Sequence[T], Iterable[T], IO]


class Mandate:
    """
    This is given to plugins when they run.
    The `Mandate` for the currently running plugin can be retrieved via the globally available `MCMD` pseudo-variable,
    hence plugin-functions do not need to constantly "relay" this value or take it as an argument (although they can
    if the designer wishes to be explicit).
    
    The `Mandate` provides the mechanism for a plugin to report progress and information back to the calling host,
    regardless of whether the host a GUI, terminal session, or another Python program.
    """
    
    
    def __init__( self, host: PluginHost, progress, plugin, args ):
        """
        CONSTRUCTOR
        
        :type args:     ArgsKwargs
        :type progress: ProgressReporter
        :type host:     Exec.PluginHost.PluginHost
        """
        self.__host = host
        self.__progress = progress
        self.__args = PluginArgValueCollection( plugin, args )
    
    
    @staticmethod
    def dead_mandate( host ):
        return Mandate( host, None, None, ArgsKwargs() )
    
    
    def print( self, message, stream: EStream = EStream.INFORMATION ):
        """
        Issues a `message` (usually a progress update) to the handling UI.
        You can also specify the nature of the message, since various UIs may handle the messages in different ways.
        (e.g. the default GUI will keep the progress window open after the process completes if any INFORMATION
        messages were received, but not if only PROGRESS messages were received)
        See the `EStream` enum for more details.
        
        :param message: Message.  
        :param stream:  Stream to send to. 
        """
        self.__progress.print( message, stream )
    
    
    def __str__( self ) -> str:
        return "Mandate({} --> {})".format( len( self.__args ), self.plugin )
    
    
    @property
    def host( self ) -> PluginHost:
        """
        Gets the host running the current plugin.

        Note: Consider using `MENV.host` instead, since `MENV.host` can be safely used _outside_ a plugin.
        
        :rtype: Exec.PluginHost.PluginHost
        """
        return self.__host
    
    
    def enumerate( self, iterable: TIterable, title: str, count: Optional[int] = None, text: TText = None ) -> Iterable[Tuple[int, T]]:
        """
        Enumerates the selection with progress feedback to the user.

        Usage is the same as the `Mandate.iterate` function.

        See the Python function `enumerate` for the return value.
        """
        return enumerate( self.iterate( iterable, title, count, text ) )
    
    
    def iterate( self, iterable: TIterable, title: str, count: Optional[int] = None, text: TText = None ) -> Iterable[T]:
        """
        Iterates over an iterable and relays the progress to the GUI.
        
        :param iterable:        What to iterate over. This can be any iterable, though special cases for `list` `tuple` and file objects allow an automated `count`. 
        :param title:           Title of the progress bar 
        :param count:           OPTIONAL. A count of how many items in the iterable. The default is len(iterable), or the length of the file in bytes (for a file object). 
        :param text:     If set the progress counter displays the string representation of the current iteration using this function.
                                    `None` : Don't print the items, just print the count 
                                    `True` : Print the string representation (same as `str` or "{0}")
                                    `Callable[[Any], str]`: Use this function to get string representations
                                    `str`: Format this string to get string representation
                                
        :return:                Yields each item from `iterable`. 
        """
        if count is None:
            try:
                count = len( iterable )
                count_is_file = False
            except TypeError:
                try:
                    original_position = iterable.tell()
                    count = iterable.seek( 0, 2 )
                    iterable.seek( original_position )
                    count_is_file = True
                except AttributeError:
                    count = 0
                    count_is_file = False
        else:
            count_is_file = False
        
        with self.action( title, count, text ) as action:
            for x in iterable:
                if count_is_file:
                    action.set_value( iterable.tell() )
                elif text:
                    action.increment()
                else:
                    action.increment()
                
                yield x
    
    
    def action( self, title: str, count: int = 0, interesting: object = None ) -> ActionHandler:
        """
        Creates an object (an `ActionHandler`) to report the current stage of work.

        This automatically sends progress messages to represent the work.
        
        For usage example and further details see the `ActionHandler` class documentation.

        :param title:       Title of the workload
        :param count:       Size of the workload, or 0 if unknown.
        :param interesting: See `iterate`
        :return:            An `ActionHandler` object that can be used to relay progress information about the workload.
        """
        return self.__progress.action( title, count, interesting )
    
    
    def warning( self, message = "" ):
        """
        See `information`.
        """
        self.print( message, EStream.WARNING )
    
    
    def log( self, message: str = "" ) -> None:
        """
        See `information`
        """
        self.print( message, EStream.PROGRESS )
    
    
    def information( self, message: str = "" ) -> None:
        """
        These convenience functions are the same as `Mandate.print` with the `stream` argument set to one of:

            * `warning` -> `WARNING`
            * `information` -> `INFORMATION`
            * `log` or `progress` -> `PROGRESS`
            * `question` -> `QUESTION`.

        See the `Mandate.print` function and the `EStream` enum for details.
        """
        self.print( message, EStream.INFORMATION )
    
    
    def progress( self, message: str = "" ) -> None:
        """
        See `information`.
        """
        self.print( message, EStream.PROGRESS )
    
    
    def question( self, message: str, options: Sequence[object] ):
        """
        Requests intervention from the user.
        Not recommended since it inconveniences the user when the plugin is run as part of a script.
        
        :param message: Message
        :param options: Options. The default is `(True,False)`, which gives a yes/no-type question. 
        :return:        The selected option.
        """
        return self.__progress.question( message, options )
    
    
    @property
    def plugin( self ):
        """
        Gets the plugin being executed
        Note: For function-based plugins (e.g. the `@command` decorator) this gets the wrapper (e.g. `CommandPlugin` for `@command`).
              In other plugins, this is a redundant alias for `self`.
        """
        return self.__args.plugin
    
    
    @property
    def args( self ) -> "PluginArgValueCollection":
        """
        Gets the arguments passed to the plugin.
        Note: This is only useful for plugin classes that generate their own dynamic arguments.
        Function-based plugins (e.g. the `@command` decorator) pass the arguments through `**kwargs`)
        """
        return self.__args
    
    
    def __iter__( self ):
        """
        Iterates over the arguments passed to the plugin
        """
        return self.args.__iter__()
    
    
    def __getitem__( self, key: PluginArg ) -> Optional[object]:
        """
        Obtains the value of the argument with the specified key
        
        :param key: Either: The `PluginArg` returned when the argument was created (preferred).
                            The string name of the argument.
        """
        return self.args[key]
    
    
    def tokwargs( self ) -> Dict[str, object]:
        """
        Converts the arguments to kwargs that can be passed to a method.
        Only the arguments of type `HFunctionParameterType[T]` are passed through, where T indicates the type passed to the function.
        
        Note: Since all plugin arguments must be named and plugins do not currently support variadic arguments, there is no equivalent `toargs`.
        """
        result = { }
        
        for arg_proxy in self.__args:
            if arg_proxy.annotation.is_mannotation_of( HFunctionParameterType ):
                result[arg_proxy.name] = arg_proxy.value
        
        return result
    
    
    @property
    def num_threads( self ):
        """
        The number of "threads" the plugin is running in.
        Note: The "threads" themselves may be processes running on separate machines.
        """
        return self.__progress.num_threads()
    
    
    @property
    def is_multithreaded( self ):
        """
        If the current operation is multi-threaded (`True`), or not (`False`).
        """
        return self.__progress.num_threads() != 1
    
    
    @property
    def is_singlethreaded( self ):
        """
        If the current operation is multi-threaded (`False`), or not (`True`).
        """
        return self.__progress.num_threads() == 1
    
    
    @property
    def is_first_thread( self ):
        """
        Convenience function that identifies if this is the first thread.
        """
        return self.__progress.thread_index() == 0
    
    
    @property
    def is_secondary_thread( self ):
        """
        Convenience function that identifies if this is not the first thread.
        """
        return self.__progress.thread_index() != 0
    
    
    @property
    def thread_index( self ):
        """
        If the current operation is multi-threaded, the index of the current thread.
        Zero-based indexing is used. This is always `0` for a single threaded plugin.
        """
        return self.__progress.thread_index()
    
    
    def divide_workload( self, quantity ) -> Tuple[int, int]:
        """
        See `MHelper.BatchList.divide_workload`.
        """
        from mhelper import batch_lists
        return batch_lists.divide_workload( self.thread_index, self.num_threads, quantity )
