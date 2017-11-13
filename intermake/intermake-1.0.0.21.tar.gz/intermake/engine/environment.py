import inspect
import warnings
from typing import Optional, List, Union, Tuple, cast, Dict

from intermake.engine import constants
from mhelper import SimpleProxy

from intermake.datastore.local_data import LocalData
from intermake.engine.mandate import Mandate
from intermake.engine.plugin_manager import PluginManager
from intermake.hosts.base import PluginHost, DMultiHostProvider, create_simple_host_provider_from_class, RunHostArgs, ERunMode
from intermake.visualisables.visualisable import IVisualisable, UiInfo, EColour
from intermake.hosts.frontends.gui_qt.designer import resources


class _DefaultRoot( IVisualisable ):
    def visualisable_info( self ) -> "UiInfo":
        return UiInfo( name = MENV.abv_name,
                       comment = MENV.name,
                       type_name = "application",
                       value = "",
                       colour = EColour.CYAN,
                       icon = resources.app,
                       extra_named = [MENV.plugins.plugins()] )


class __Environment:
    """
    intermake Environment
    
    For consistency of documentation, all fields are accessed through properties.
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        All parameters are defaulted.
        """
        self.__name: str = constants.DEFAULT_NAME
        self.__version: str = "0.0.0.0"
        self.__abbreviated_name: Optional[str] = None
        self.__root: Optional[IVisualisable] = _DefaultRoot()
        self.__constants: Dict[str, str] = { }
        self.__plugins: PluginManager = PluginManager()
        self.__local_data: LocalData = LocalData()
        self.__host_provider: DMultiHostProvider = None
        self.__host: PluginHost = None
        self.__is_locked: bool = False
        setattr( self, "frozen", None )
    
    
    @property
    def is_locked( self ) -> bool:
        """
        Gets or sets whether the environment has been configured.
        This prevents a second application overwriting the first if, for some reason, they are both imported. 
        """
        return self.__is_locked
    
    
    @is_locked.setter
    def is_locked( self, value: bool ):
        self.__is_locked = value
    
    
    def __setattr__( self, key: str, value: object ) -> None:
        """
        Prohibits new attributes being set on this class.
        This guards against functionless legacy setup.  
        """
        if hasattr( self, "frozen" ) and not hasattr( self, key ):
            raise TypeError( "Unrecognised attribute on «{}»".format( type( self ) ) )
        
        object.__setattr__( self, key, value )
    
    
    @property
    def name( self ) -> str:
        """
        Gets or sets the name of the application. 
        """
        return self.__name
    
    
    @name.setter
    def name( self, value: str ):
        if self.__warn_if_locked( "name" ):
            return
        
        if not value:
            raise ValueError( "The name may not be empty." )
        
        self.__name = value
        self.__constants["APP_NAME"] = self.__name
        self.__constants["APP_ABV"] = self.__name
    
    
    @property
    def plugins( self ) -> PluginManager:
        """
        Gets the Plugin manager, that allows you to view available plugins and register new ones.
        See class: `PluginManager`
        """
        return self.__plugins
    
    
    @property
    def local_data( self ) -> LocalData:
        """
        Obtains the local data store, used to apply and retrieve application settings.
        See class: `LocalData`
        """
        return self.__local_data
    
    
    @property
    def constants( self ) -> Dict[str, str]:
        """
        Obtains the constant dictionary, used to replace $(XXX) in documentation strings.
        """
        return self.__constants
    
    
    @property
    def host( self ) -> PluginHost:
        """
        Gets or sets the current plugin host.
        See class: `PluginHost`.
        """
        return self.__host
    
    
    @host.setter
    def host( self, value: PluginHost ):
        self.__host = value
    
    
    @property
    def root( self ) -> Optional[IVisualisable]:
        """
        Gets or sets the application root.
        Allows the user to traverse the application hierarchy.
        If `None`, that feature will be disabled.
        See class: `IVisualisable`. 
        """
        return self.__root
    
    
    @root.setter
    def root( self, value: Optional[IVisualisable] ):
        if self.__warn_if_locked( "root" ):
            return
        
        self.__root = value
    
    
    @property
    def host_provider( self ) -> DMultiHostProvider:
        """
        Gets or sets the host provider.
        This is used by some core commands to suggest a new host for the various UI modes.
        See field: `DMultiHostProvider`.
        """
        if self.__host_provider is None:
            from intermake.hosts.console import ConsoleHost
            
            def __gui() -> PluginHost:
                from intermake.hosts.gui import GuiHost
                return GuiHost()
            
            
            self.__host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui )
        
        return cast( DMultiHostProvider, self.__host_provider )
    
    
    @host_provider.setter
    def host_provider( self, value: DMultiHostProvider ):
        self.__host_provider = value
    
    
    @property
    def version( self ) -> str:
        """
        Gets or sets the application version.
        If this starts with a `0.`, intermake will assume this is an alpha version and include a warning message in the application's banner. 
        """
        return self.__version
    
    
    @version.setter
    def version( self, value: Union[str, List[int], Tuple[int]] ):
        if self.__warn_if_locked( "version" ):
            return
        
        if not isinstance( value, str ):
            value = ".".join( str( x ) for x in value )
        
        self.__version = value
        self.__constants["APP_VERSION"] = self.__version
    
    
    @property
    def abv_name( self ) -> str:
        """
        Gets or sets the abbreviated name of the application.
        The abbreviated name is used in place of the application name in certain places.
        If this is `None`, the non-abbreviated `name` is returned.
        """
        return self.__abbreviated_name or self.name
    
    
    @abv_name.setter
    def abv_name( self, value: Optional[str] ) -> None:
        if self.__warn_if_locked( "abv_name" ):
            return
        
        self.__abbreviated_name = value
        self.__constants["APP_ABV"] = self.__version
    
    
    def __warn_if_locked( self, property_name: str ) -> bool:
        """
        If the environment `is_locked`, this function displays a warning.
        
        :returns `is_locked`.
        """
        if self.is_locked:
            warnings.warn( "A new package is attempting to modify the environment's «{}», but the environment has already been configured. Did you accidentally try to import an unrelated intermake package? The workspace may now be corrupt and so the application will exit. If the called package should be compatible with the current package, the the package author should consider checking `MENV.is_locked` and handling appropriately.".format( property_name ) )
            exit( 1 )
        
        return self.is_locked


# noinspection SpellCheckingInspection
MENV = __Environment()  # type: __Environment
"""
Obtains the intermake "core". See the `__Environment` docs for more details.
To modify the environment, modify the fields on `MENV`. `MENV` itself should not be replaced.
"""


def __current_mandate() -> Mandate:
    """
    See field: `MCMD`.
    """
    if MENV.host is None:
        return cast( Mandate, None )
    
    return MENV.host._get_mandate()


# noinspection SpellCheckingInspection
MCMD = cast( Mandate, SimpleProxy( __current_mandate ) )
"""
This is a proxy for the `Mandate` in use by the current plugin.

Its execution outside of plugins undefined.

Functions that aren't plugins (i.e. that have the `@command` decorator, or are contained within a `Plugin`-derived class) can use the `@mandated`
decorator to alert the user that they require `MCMD` and thus must be run from within a plugin. More explicitly, they can take the `Mandate`
as one of their arguments.
"""


def start( caller: Optional[str] = None ):
    """
    Quickly starts up intermake.
    
    :param caller:        Name of caller (i.e. __name__), used to start the CLI (ERunMode.ARG) if this is "__main__".
                          * If you have added your own check, or wish to force the CLI to start then you do not need to supply this argument.
                          * If you do not wish the CLI to start, do not call this function.
    """
    if MENV.name == constants.DEFAULT_NAME:
        raise ValueError( "Preventing `quick_start` call without setting the `MENV.name`: This probably means that your `__init__` has not been called." )
    
    if caller is None or caller == "__main__":
        MENV.host = MENV.host_provider( ERunMode.ARG )
        
        MENV.host.run_host( RunHostArgs( read_argv = True, can_return = False ) )


def register( plugin: object ) -> None:
    frame = inspect.stack()[1]
    module_ = inspect.getmodule( frame[0] )
    
    from intermake.engine.plugin import Plugin
    assert isinstance( plugin, Plugin )
    MENV.plugins.register( plugin, module_ )
