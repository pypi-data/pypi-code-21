"""
Contains the `CommandPlugin` class, as well as the related decorator `command`.
Also contains the derived `HelpPlugin` and the `help_command` decorator.
"""

import sys
import inspect
from typing import List, Optional, Union

from colorama import Style, Back, Fore

from intermake.engine import constants
from intermake.engine.constants import EThread, OUVisibility
from intermake.engine.environment import MENV
from intermake.engine.function_inspector import FnInspect, IFunction
from intermake.engine.plugin import NoCallError, Plugin
from mhelper import override


__author__ = "Martin Rusilowicz"


def command( _fn = None,
             *,
             names: Optional[Union[str, List[str]]] = None,
             description: Optional[str] = None,
             type_name: Optional[str] = None,
             threading: Optional[EThread] = None,
             visibility: OUVisibility = None,
             highlight: OUVisibility = None,
             true_function = None,
             register: bool = True ):
    """
    DECORATOR FOR FUNCTION OR CLASS.
    
    For a function:
        The function is wrapped in the `CommandPlugin` class, below.
        See `Plugin.__init__` for argument descriptions, with the exception of the `register` argument, that automatically registers the plugin with the host when set.
    
        This decorator is primarily used to allow the user to access functions as "plugins", but can also be used to quickly add support for asynchronous support to a function.
        
        ```
        @command()
        def spam( a : int ) -> None:
            . . .
            
        @command(names = ["eggs", "beans"]):
        def beans( a : str ) -> None:
            . . .
        ```
        
    For a class:
        An instance of the class is registered with the host.
        Since the classes constructor call `Plugin.__init__`, no other arguments should be passed to the `command` decorator.
        If constructor arguments need to be passed, the caller should instead create their instance manually and call `MENV.plugins.register` on that instance.
    """
    
    
    def ___command( fn ):
        from intermake.engine.environment import MENV
        
        v = 10
        c = len( MENV.plugins.all_plugins() )
        cc = c % v
        
        name = ((MENV.name if MENV.name != constants.DEFAULT_NAME else "System") + "/" + fn.__name__).ljust( 50 ) + " ▌" + "█" * cc + "▓" + "▒" * (v - cc) + "▐ " + str( c )
        print( Back.YELLOW + Fore.BLACK + name + Style.RESET_ALL, end = "", file = sys.stderr )
        sys.stderr.flush()
        
        if not inspect.isfunction( fn ):
            plugin = fn()
            fn.instance = plugin
        else:
            plugin = CommandPlugin( names = names,
                                    description = description,
                                    type_name = type_name,
                                    threading = threading,
                                    visibility = visibility,
                                    function = fn,
                                    true_function = true_function,
                                    highlight = highlight )
        
        if register:
            frame_ = inspect.stack()[1]
            module_ = inspect.getmodule( frame_[0] )
            MENV.plugins.register( plugin, module_ )
        
        print( "\r" + " " * len( name ) + "\r", end = "", file = sys.stderr )
        
        if not inspect.isfunction( fn ):
            return fn
        else:
            return plugin
    
    
    if _fn is not None:
        return ___command( _fn )
    else:
        return ___command


class CommandPlugin( Plugin ):
    """
    Wraps a function into an Plugin object.
    """
    
    
    def __init__( self,
                  *,
                  names: Optional[Union[str, List[str]]] = None,
                  description: Optional[str] = None,
                  type_name: Optional[str] = None,
                  threading: Optional[EThread] = None,
                  visibility: OUVisibility = None,
                  function: IFunction,
                  true_function = None,
                  highlight: OUVisibility = None,
                  folder: Optional[str] = None ):
        """
        Constructor.
        See `Plugin.__init__` for argument descriptions.
        
        Note that several of the arguments get defaults from the function via reflection, if not provided.
        
        :param names: Default name is the function name
        :param function: Function to call.
                            Plugin arguments are constructed via reflection, hence this must be a fully annotated function.
                            Any argument named `self` is ignored.
        :param description: Default description is the function documentation
        :param true_function: Function to call. `function` is then only used for the reflection stage. If `None`, `function` is used for reflection and calling.
        """
        self.function_info = FnInspect( function )
        
        if not names:
            name = function.__name__  # type: str
            name = name.strip( "_" )
            names = [name]
        
        super().__init__( names = names,
                          description = description or self.function_info.description,
                          type_name = type_name or constants.PLUGIN_TYPE_COMMAND,
                          threading = threading,
                          visibility = visibility,
                          highlight = highlight,
                          folder = folder )
        
        function_info = self.function_info
        
        self._mandate_name = self._add_args_from_function( function_info )
        
        if true_function is not None:
            self.function = true_function  # type: IFunction
        else:
            self.function = function  # type: IFunction
        
        assert hasattr( self.function, "__call__" ), "Command plugin requires a callable object, but this object is not callable. The offending object is «{0}».".format( self.function )
    
    
    def __call__( self, *args, **kwargs ):
        """
        INHERITED
        This method exists to allow a function decorated by encapsulation in this class (i.e. using `@command()`) to be called as if the decorator had never been added.
        """
        
        # Try to run the plugin from within another
        try:
            return super().__call__( *args, **kwargs )
        except NoCallError:
            # noinspection PyCallingNonCallable
            return self.function( *args, **kwargs )
    
    
    @override
    def virtual_run( self ) -> Optional[object]:
        """
        INHERITED
        """
        from intermake.engine.environment import MCMD
        kwargs_ = MCMD.tokwargs()
        
        if self._mandate_name:
            kwargs_[self._mandate_name] = MCMD
        
        # noinspection PyCallingNonCallable
        return self.function( **kwargs_ )


class HelpPlugin( CommandPlugin ):
    """
    Special case of `CommandPlugin` that just shows help.
    
    The help-text is obtained by calling the function itself.
        * Return `None` or `""` to use the documentation of the function (`__doc__`).
        * Use `$(DOC)` in the returned text to include the documentation inline.
        * The function can return any object coercible to `str`.
    
    Since the function is use to obtain the help text, rather than being called by the user, it cannot not take any parameters.
    """
    
    
    def __init__( self, *, function: IFunction ):
        super().__init__( function = function, visibility = False )
    
    
    def virtual_run( self ):
        from intermake.engine.environment import MCMD
        from intermake.engine import cli_helper
        MCMD.print( cli_helper.get_details_text( self ) )
    
    
    def get_description( self ):
        provided = self.function()
        
        if not provided:
            provided = super().get_description()
        else:
            provided = str( provided )
            
            if "$(DOC)" in provided:
                provided = provided.replace( "$(DOC)", super().get_description() )
        
        return provided


def help_command( register = True, **kwargs ):
    """
    Decorator for help plugins. Help plugins specify the help-text in their doc-comments and/or generate it dynamically.
    See `HelpPlugin` for more details.
    
    :param register: When set, registers the plugin with the `intermake` environment.
    :param kwargs: Passed to `HelpPlugin` constructor.
    """
    
    
    def __command( fn ):
        # noinspection PyArgumentList
        plugin = HelpPlugin( function = fn, **kwargs )
        
        if register:
            MENV.plugins.register( plugin )
        
        return plugin
    
    
    return __command
