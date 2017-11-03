import inspect
import warnings
from typing import Optional

from colorama import Fore

from intermake.engine.environment import MCMD
from intermake.engine.function_inspector import FnInspect
from intermake.engine.mandate import PluginArg
from mhelper.comment_helper import abstract, override, sealed, virtual

from intermake.engine.plugin import Plugin
from intermake.engine import constants, function_inspector, cli_helper
from intermake.engine.constants import OUVisibility, EThread


def setter_command( name = None, description = None, visibility = None ):
    def __decorator( fn ):
        return __SetterPluginViaFunction( fn, name, description, visibility )
    
    
    return __decorator


@abstract
class SetterPlugin( Plugin ):
    """
    Base class for a plugin that sets values on an object.
    
    Derived class should override `get_target` to indicate the target that will be manipulated.
    May also optionally override `set_target` if the target needs saving after modification.
    """
    
    
    def __init__( self, name: str, description: str, visibility: OUVisibility = None, highlight: OUVisibility = None ):
        """
        Constructor. Takes the normal plugin arguments
        :param name: See `Plugin` 
        :param description: See `Plugin`   
        :param visibility: See `Plugin` 
        """
        super().__init__( names = name,
                          description = description,
                          type_name = constants.PLUGIN_TYPE_COMMAND,
                          threading = EThread.SINGLE,
                          visibility = visibility,
                          highlight = highlight )
        
        self.__populated = False
    
    
    @virtual
    def format_key( self, key: str ) -> Optional[str]:
        """
        Given the `key` property, returns the name of the associated parameter, or `None` if the parameter should be hidden.
        The default implementation returns the key verbatim.
        """
        return key
    
    
    @abstract
    def get_sample( self ) -> object:
        """
        Obtains the sample object from which the available properties should be deduced.
        This is called only once - the first time the plugin is run (`virtual_run`) or the help text (`description`) is requested. 
        :return: 
        """
        raise NotImplementedError( "abstract" )
    
    
    @property
    def args( self ):
        self.__populate()
        return super().args
    
    
    def __populate( self ):
        """
        Called to populate the lookup table `__argument_to_property`.
        """
        if self.__populated:
            return
        
        sample = self.get_sample()
        
        for arg in self.extract_arguments( sample, self.format_key ):
            self._add_argument( arg )
        
        self.__populated = True
    
    
    @staticmethod
    def extract_arguments( sample, formatter = str ):
        """
        Extracts the arguments from a sample's fields.
        :param sample: 
        :param formatter: 
        :return: The list of arguments. Each of these arguments "arg" is provided with an additional member:
        
            Name:    .tag_field_name
            Type:    str
            Purpose: Provides the name of the field to which the argument refers. 
        
        """
        args = []
        
        if sample is None:
            return args
        
        documentation_dict = { }
        
        for x in inspect.getmro( type( sample ) ):
            documentation_dict.update( function_inspector.extract_documentation( x.__doc__, "data" ) )
        
        for field_name, field_value in sample.__dict__.items():
            if field_name.startswith( "_" ):
                continue
            
            argument_name = formatter( field_name )
            
            if not argument_name:
                continue
            
            documentation = documentation_dict.get( field_name )
            
            if documentation is None:
                msg = "A SetterPlugin references the field " + Fore.YELLOW + "`{}::{}`" + Fore.RESET + " (under the name `{}`) on the sample object «{}», but does not provide any documentation for that field."
                warnings.warn( msg.format( type( sample ).__name__, field_name, argument_name, sample ), UserWarning )
                documentation = "Not documented :("
            
            arg = PluginArg( argument_name, Optional[type( field_value )], None, documentation )
            arg.tag_field_name = field_name
            
            args.append( arg )
        
        return args
    
    
    @abstract
    def get_target( self ) -> object:
        """
        Derived class must provide the target to be modified.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def set_target( self, target: object ):
        """
        After modification, derived class may save the target.
        """
        pass
    
    
    @sealed
    def get_description( self ):
        """
        OVERRIDE to ensure the the parameters are populated before returning the description.
        """
        return super().get_description()
    
    
    @override
    @sealed
    def virtual_run( self ):
        """
        Sets the specified value(s).
        """
        set_one = False
        msg = []
        target = self.get_target()
        
        for arg in MCMD.args:
            if arg.value is not None:
                if hasattr( arg.arg, "tag_field_name" ):
                    field_name = arg.arg.tag_field_name
                    target.__dict__[field_name] = arg.value
                    msg.append( cli_helper.format_kv( arg.name, arg.value, "-->" ) )
                    set_one = True
        
        if not set_one:
            for field_name in sorted( target.__dict__.keys() ):
                name = self.format_key( field_name )
                msg.append( cli_helper.format_kv( name, target.__dict__[field_name] ) )
        else:
            self.set_target( MCMD, target )
        
        MCMD.information( "\n".join( msg ) )


class __SetterPluginViaFunction( SetterPlugin ):
    def get_sample( self ) -> object:
        return self.function.return_type
    
    
    def get_target( self ) -> object:
        kwargs = MCMD.tokwargs()
        
        for arg in MCMD.args:
            if hasattr( arg, "tag_field_name" ):
                del kwargs[arg.name]
        
        return self.function.call( **kwargs )
    
    
    def __init__( self, fn, name: Optional[str], description: Optional[str], visibility: OUVisibility ):
        self.function = FnInspect( fn )
        
        if self.function.return_type is None:
            raise ValueError( "A setter command «{}» has been created, but the return type has not been specified. This is probably an error so the execution has been halted.".format( self.function.name ) )
        
        super().__init__( name or self.function.name, description or self.function.description, visibility )
