import warnings
from typing import Callable, List, Optional, Union, cast
from mhelper import array_helper, exception_helper, string_helper, abstract, override, protected, virtual

from intermake.engine import constants
from intermake.engine.async_result import AsyncResult
from intermake.engine.constants import EThread, OUVisibility, mandated
from intermake.engine.function_inspector import FnInspect
from intermake.engine.mandate import ArgsKwargs, HFunctionParameterType, Mandate, PluginArg
from intermake.engine.plugin_manager import PluginFolder
from intermake.engine.progress_reporter import ProgressReporter
from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo


__author__ = "Martin Rusilowicz"


class NoCallError( Exception ):
    pass


class PartialSuccess( Exception ):
    """
    A plugin may circumnavigate the normal return procedure and return a successful result via an exception.
    """
    
    
    def __init__( self, message = None, result = None ):
        self.result = result
        
        if not message:
            message = "The thread terminated because it has saved or has already created its workload. The primary thread will pick it up. This is not an error."
        
        super().__init__( message )


_unnamed_count = 0


@abstract
class Plugin( IVisualisable ):
    """
    Plugins are things that can be run by the user.
    They appear in the "Plugins" section of the main screen in the GUI and can also be invoked from the command line.
    See readme.md in this directory for details.
    """
    
    FOLDER_DELIMITER = "/"
    
    
    def __init__( self,
                  *,
                  names: Optional[ Union[ str, List[ str ] ] ] = None,
                  description: Optional[ str ] = None,
                  type_name: Optional[ str ] = None,
                  threading: Optional[ EThread ] = None,
                  visibility: OUVisibility = None,
                  highlight: OUVisibility = None,
                  folder: Optional[ str ] = None ):
        """
        CONSTRUCTOR
        :param names:           Name or names of the plugin. Mandatory.
        :param description:     Description of the plugin. Mandatory.
        :param type_name:       Name of the plugin type. Defaults to `constants.PLUGIN_TYPE_COMMAND`.
        :param threading:       Threading hint for the plugin. Defaults to `EThread.SINGLE`. 
        :param visibility:      Visibility of the plugin (see `OUVisibility`).
        :param highlight:       A highlighted function gets emphasis on the command explorer.
                                See `OUVisibility`.
        :param folder:          Optional folder where the plugin resides.
                                Esoteric use - plugins automatically collect this from the module anyway.
        """
        
        names = array_helper.as_sequence( names or None, cast = list )
        
        if not names:
            raise ValueError( "A plugin must have at least one name." )
        
        if threading is None:
            threading = EThread.SINGLE
        
        visibility = self.__vis_to_fun( visibility, True )
        highlight = self.__vis_to_fun( highlight, False )
        
        if type_name is None:
            type_name = constants.PLUGIN_TYPE_COMMAND
        
        if not description:
            # Not having a description is probably a mistake
            description = "Not documented :("
            warnings.warn( "A plugin «{}» has no description.".format( names ) )
        
        exception_helper.assert_instance( "description", description, str )
        exception_helper.assert_instance( "type_name", type_name, str )
        exception_helper.assert_instance( "threading", threading, EThread )
        
        self.names = names  # type: List[str]
        self.__description = string_helper.fix_indents( description )
        # noinspection PyUnresolvedReferences
        self.__children = [ ]  # type: List[Plugin]
        self.__args = [ ]  # type: List[PluginArg]
        self.__type_name = type_name
        self.__threading = threading
        self.parent = None  # type: Union[Plugin, PluginFolder]
        self.__visibility = visibility  # type: Callable[[], bool]
        self.__highlight = highlight  # type: Callable[[], bool]
        self.__dict__[ "__doc__" ] = description
        self.folder = folder
    
    
    @staticmethod
    def __vis_to_fun( visibility, default ):
        if visibility is None:
            visibility = default
        
        if isinstance( visibility, bool ):
            visibility = (lambda closure: lambda: closure)( visibility )
        
        return visibility
    
    
    @property
    def name( self ) -> str:
        return self.names[ 0 ]
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.get_description(),
                       type_name = "Plugin",
                       value = self.get_plugin_type(),
                       colour = EColour.RED,
                       icon = resources.command,
                       extra = { "arguments": self.__args,
                                 "children" : self.__children } )
    
    
    @property
    def is_visible( self ) -> bool:
        return self.__visibility()
    
    
    @property
    def is_highlighted( self ) -> bool:
        return self.__highlight()
    
    
    @property
    def visibility( self ) -> bool:
        warnings.warn( "deprecated, use is_visible", DeprecationWarning )
        return self.__visibility()
    
    
    @property
    def visibility_function( self ) -> Callable[ [ ], bool ]:
        return self.__visibility
    
    
    @override
    def __call__( self, *args, **kwargs ):
        """
        INHERITED
        This method exists to allow a function decorated by encapsulation in this class (i.e. using `@command()`) to be called as if the decorator had never been added.
        It has now been added to the base Plugin class to allow all plugins to be called in this manner.
        """
        return self.run( *args, **kwargs )
    
    
    def get_plugin_type( self ) -> str:
        """
        Name of the type associated with this plugin
        """
        return self.__type_name
    
    
    @virtual
    @property
    def args( self ) -> List[ PluginArg ]:
        """
        Returns the set of arguments for this plugin. See `PluginArg`.
        
        Derived classes may override this method, if providing arguments dynamically.
        """
        return self.__args
    
    
    def find_arg( self, name: str ) -> PluginArg:
        """
        Returns the specified argument. See `PluginArg`.
        """
        from intermake.engine.environment import MENV
        
        host = MENV.host
        friendly_name = host.translate_name( name )
        
        for arg in self.args:
            if host.translate_name( arg.name ) == friendly_name:
                return arg
        
        raise KeyError( "There is no argument named «{}» in «{}».".format( name, self ) )
    
    
    @protected
    def _add_argument( self, argument: PluginArg ) -> None:
        """
        Adds a user-controllable argument to the plugin.
        See also _add_arg().
        """
        self.__args.append( argument )
    
    
    @protected
    def _add_arg( self, name: str, type, default, description ) -> PluginArg:
        """
        Adds a user-controllable argument to the plugin.
        """
        result = PluginArg( name, type, default, description )
        self.__args.append( result )
        return result
    
    
    @protected
    def _add_args_from_function( self, function_info: FnInspect ):
        mandate_name = None
        
        for arg in function_info.args:
            if not arg.description:
                if arg.name == "self":
                    arg.description = "internal"
                else:
                    warnings.warn( "An argument «{}» on «{}» has no description.".format( arg.name, self.function_info ), UserWarning )
            
            if (arg.type is Mandate) or (arg.name == "mandate"):
                raise ValueError( "Legacy code detected. Plugins should not take a `mandate` parameter." )
            
            if arg.name != "self":
                self._add_arg( arg.name, HFunctionParameterType[ arg.type], arg.default, arg.description )
        
        return mandate_name
    
    
    @override
    def __str__( self ) -> str:
        """
        String representation
        """
        return self.name
    
    
    @override
    def __repr__( self ):
        if self.name.endswith( "help" ):  # TODO: Magic
            return "This is a function named «{0}». Please type '{0}()' to run this function.".format( self.name )
        else:
            return "This is a function named «{0}». Please type '{0}()' to run this function, or type '{0}.help()' for more information.".format( self.name )
    
    
    def help( self ):
        """
        For Python interface - shows the help on this plugin.
        """
        _intermake_internal_show_help( self )
    
    
    @virtual
    def get_description( self ) -> str:
        """
        Description of the executable
        
        Derived classes may override this to provide a dynamic description
        """
        return self.__description
    
    
    def children( self ) -> "List[Plugin]":
        """
        Executables can nest each other if they are related in some way, this is a list of this one's children
        """
        return self.__children
    
    
    def args_to_kwargs( self, *args ):
        """
        Given a set of arguments appearing in the same order as the arguments for this executable, produces
        a kwargs dictionary compatible with Plugin.run(), Plugin.modify(), Plugin.copy() etc.
        """
        result = { }
        
        if not args:
            return result
        
        arg_list = list( self.args )
        
        if len( args ) > len( arg_list ):
            raise KeyError( "Cannot convert a positional argument list of length {0} to a key-value argument list of length {1}.".format( len( args ), len( arg_list ) ) )
        
        for i, v in enumerate( args ):
            if v is not None:
                result[ arg_list[ i ].name ] = v
        
        return result
    
    
    def run( self, *args, callback: Optional[ Callable[ [ AsyncResult ], None ] ] = None, _sync = False, **kwargs ) -> Optional[ object ]:
        """
        Finds the host and runs the Plugin.
        Use this to run plugins because it performs checking - don't try to get the host from anywhere else and run it manually!
        
        :param _sync:    Always runs the plugin synchronously. Used internally.
        :param callback: An optional callback to call with the results. If not specified the default results handler for the host will be used.
        :param kwargs: Arguments to pass to the plugin. Values specified here override those in args, if provided.
        :return Ignore. This returns the result from the host after being told to execute the plugin (this is NOT the same as the result of the execution).
                    For GuiHost this is normally `None` (because it is async, but could be a wait handle, etc.)
                    For ConsoleHost this is indeed the result (because it actually runs synchronously). Use cautiously.
        """
        # Set arguments if necessary
        plugin_args = ArgsKwargs( *args, **kwargs )
        
        # Ask the host to call run our main functionality
        from intermake.engine.environment import MENV
        host = MENV.host
        return host.call_virtual_run( self, plugin_args, callback, _sync )  # ---> self.call_virtual_run()
    
    
    @mandated
    def call_virtual_run( self ) -> Optional[ object ]:
        """
        Called by the host to run the plugin's actual functionality.
        :return: Result of virtual_run(). 
        """
        try:
            result = self.virtual_run()
        except PartialSuccess as ex:
            from intermake.engine.environment import MCMD
            MCMD.print( "The operation has ended early with partial success: {}".format( ex ) )
            return ex.result
        
        return result
    
    
    @abstract
    @mandated
    def virtual_run( self ) -> Optional[ object ]:
        """
        Implemented by the derived class, implements the Plugin's main functionality
        
        :return: A plugin specific value.
                 
                 For user-invoked plugins this should generally be something the plugin host (GUI or CLI) can handle.  
                 Types generally handled are:
                    Simple types (`str`, `int`, `float`, `bool`, etc.), that can be displayed to std.out. or in a message-box.
                    `DocketFolder` or `Docket` items, that are created from database queries and can be saved to the user's dockets.
                     
                 For internal plugins, the return type can be any information relayed from one plugin to another.
        """
        raise NotImplementedError( "Abstract" )
    
    
    def set_description( self, value: str ):
        """
        Changes the description() of this plugin.
        """
        self.__description = value
    
    
    def set_type_name( self, value: str ):
        """
        Changes the type_name() of this plugin.
        """
        self.__type_name = value
    
    
    def add_child( self, child_plugin: "Union[Plugin, PluginFolder]" ) -> None:
        """
        Adds a "child" plugin (a related plugin)
        """
        child_plugin.__parent = self
        self.__children.append( child_plugin )
    
    
    def remove_child( self, child_plugin: "Union[Plugin, PluginFolder]" ):
        self.__children.remove( child_plugin )
    
    
    def threading( self ) -> EThread:
        """
        Threading model, used by `PluginHost` derivatives to manage threads. See `EThread` for details.
        """
        return self.__threading


class FunctionPlugin( Plugin ):
    """
    A plugin that wraps a function.
    For internal use only (never visible to user).
    """
    
    
    def __init__( self, title: Optional[ str ], function: Callable[ [ ], object ] ):
        super().__init__( names = title, type_name = "Function", visibility = False )
        self.__function = function  # type: Callable[ [ ProgressReporter ], object ]
    
    
    def virtual_run( self ) -> Optional[ object ]:
        return self.__function()


class SecondaryError( Exception ):
    pass


class __intermake_internal_show_help_type( Plugin ):
    """
    Help (internal)
    """
    
    
    def virtual_run( self ) -> Optional[ object ]:
        from intermake.engine import cli_helper
        from intermake.engine.environment import MCMD
        
        command = MCMD.args[ self.arg ]
        MCMD.print( cli_helper.get_details_text( cast( Plugin, command ) ) )
        return None
    
    
    def __init__( self ) -> None:
        super().__init__( names = type( self ).__name__,
                          description = "Shows help",
                          type_name = "internal command",
                          visibility = False )
        self.arg = self._add_arg( "plugin", Optional[ Plugin ], None, "command to show help for" )


_intermake_internal_show_help = __intermake_internal_show_help_type()
