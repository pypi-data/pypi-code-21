import warnings
from collections import OrderedDict
from typing import Dict, Iterator, List, Optional

from intermake.engine.function_inspector import NOT_PROVIDED
from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo
from mhelper import string_helper, AnnotationInspector, MAnnotationFactory


class ArgsKwargs:
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs


class PluginArg( IVisualisable ):
    """
    Defines an argument that a user can set on an `Plugin` to determine how it behaves.

    These objects define only what arguments are accepted, and do not contain the actual user-supplied value
    - see`PluginArgValue` for that.
    """
    
    
    def __init__( self, name: str, type_, default, description ):
        """
        CONSTRUCTOR
        :param name: Name of the argument
        :param type_: Type the argument takes
        :param default: Default value of the argument
        """
        assert name, "A plugin argument must have a name"
        assert type_, "A plugin argument «{0}» must have a type".format( name )
        
        if not description:
            description = "Not documented :("
        
        self.name = name
        self.__annotation = AnnotationInspector( type_ )
        self.__default = default
        self.__description = string_helper.fix_indents( description )
        self.plugin = None
    
    
    def __hash__( self ) -> int:
        return hash( self.name )
    
    
    def __eq__( self, other ):
        return self.name == other.name
    
    
    def __repr__( self ) -> str:
        return "PluginArg({} : {})".format( self.name, self.annotation )
    
    
    def __str__( self ) -> str:
        return self.name
    
    
    def get_value( self ) -> "PluginArgValue":
        """
        Gets the current value of the argument.
        Result undefined when when called inside a plugin.
        """
        from intermake.engine.environment import MCMD
        return MCMD.args[self]
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.description,
                       type_name = "arg",
                       value = str( self.annotation ),
                       colour = EColour.CYAN,
                       icon = resources.unknown,
                       extra = { "type"   : self.annotation,
                                 "default": self.default } )
    
    
    @property
    def can_be_none( self ) -> bool:
        return self.__annotation.is_optional
    
    
    @property
    def description( self ) -> str:
        """
        Description of the argument
        """
        return self.__description
    
    
    def get_formatted_description( self ) -> str:
        from intermake.engine.environment import MENV
        return MENV.host.substitute_text( self.description )
    
    
    @property
    def default( self ) -> Optional[object]:
        """
        Default value of the argument
        """
        return self.__default
    
    
    @property
    def type( self ) -> type:
        """
        Type of the argument
        """
        warnings.warn( "Use annotation instead.", DeprecationWarning )
        return self.__annotation.value
    
    
    @property
    def annotation( self ) -> AnnotationInspector:
        return self.__annotation
    
    
    @property
    def type_description( self ) -> str:
        """
        Combines the type and hint into a descriptive name
        """
        warnings.warn( "Use annotation instead.", DeprecationWarning )
        return str( self.__annotation )
    
    
    def __error_details( self ):
        return " Details: name = {}, annotation = {}, default = {} {}".format( self.name, self.annotation, type( self.__default ), self.__default )


class PluginArgValue:
    """
    An extension of `PluginArg` that contains the user-supplied value for the argument.
    """
    
    
    def __init__( self, arg: PluginArg ):
        assert isinstance( arg, PluginArg )
        
        self.__arg = arg
        self.__value = arg.default
    
    
    @property
    def arg( self ):
        return self.__arg
    
    
    @property
    def name( self ) -> str:
        return self.__arg.name
    
    
    @property
    def type( self ) -> type:
        warnings.warn( "Deprecated - Use annotation", DeprecationWarning )
        return self.__arg.annotation.value
    
    
    @property
    def annotation( self ) -> AnnotationInspector:
        return self.__arg.annotation
    
    
    @property
    def value( self ) -> Optional[object]:
        """
        Current value of the argument
        """
        return self.__value
    
    
    @property
    def is_set( self ) -> bool:
        """
        If the argument has been set
        """
        return self.__value is not NOT_PROVIDED
    
    
    def set_value( self, value: Optional[object] ) -> None:
        """
        Sets the value of the argument
        """
        if not self.annotation.is_viable_instance( value ):
            raise TypeError( "Trying to set the value «{}» on the plugin argument «{}»:«{}» but the value is {} and the argument is {}.".format( value, self.__arg.plugin, self.name, type( value ), self.annotation ) )
        
        self.__value = value


class PluginArgValueCollection:
    """
    Manages a set of arguments (`PluginArg`s) and their values,
    as a collection of `PluginArgValue` objects.
    """
    
    
    def __init__( self, plugin, args: ArgsKwargs ):
        """
        CONSTRUCTOR
        :param plugin:  Plugin this collection is for
        :param args:    Values to apply to the arguments
        """
        self.__plugin = plugin
        self.__args = OrderedDict()  # type:Dict[PluginArg, PluginArgValue]
        
        for arg in self.__plugin.args:
            self.__args[arg] = PluginArgValue( arg )
        
        self.set( args )
        
        incomplete = self.incomplete()
        
        if incomplete:
            raise ValueError( "Cannot run the «{0}» plugin because the following arguments have not been provided:\n{1}".format( plugin.name, "\n".join( [("    * " + x.name) for x in incomplete] ) ) )
    
    
    @property
    def plugin( self ):
        """
        Returns the plugin to which this set of arguments is being applied.
        :return: An object of type `Plugin`.
        :rtype:  Plugin
        """
        return self.__plugin
    
    
    def __len__( self ):
        return len( self.__args )
    
    
    def __iter__( self ) -> "Iterator[PluginArgValue]":
        """
        Iterates over this `PluginArgValue` collection.
        """
        return self.__args.values().__iter__()
    
    
    def __getitem__( self, key: PluginArg ) -> Optional[object]:
        """
        Equivalent to `get_arg`, but returns the value on the `PluginArgValue`.
        """
        return self.get_arg( key ).value
    
    
    def __setitem__( self, key: PluginArg, value: Optional[object] ) -> None:
        """
        Sets the value of the argument with the specified key.
        See `PluginArgValue.set_value` for details on accepted values.

        :param key:     A `PluginArg`. Unlike `get` a name is not accepted.
        :param value:   The value to apply.
        """
        self.__set_arg( key, value )
    
    
    def get_arg( self, key: PluginArg ) -> "PluginArgValue":
        """
        Retrieves the `PluginArgValue` of the specified `PluginArg` or `str` (name).

        :except KeyError:  If the argument does not exist
        :except TypeError: If the argument is not a `PluginArg` or `str`.
        """
        if isinstance( key, PluginArg ):
            try:
                return self.__args[key]
            except KeyError as ex:
                raise KeyError( "The plugin «{}» has no argument «{}» in «{}».".format( self.plugin, key, ", ".join( x.name for x in self.__args ) ) ) from ex
        elif isinstance( key, str ):
            for arg in self.__args.values():  # type: PluginArgValue
                if arg.name == key:
                    return arg
            
            raise KeyError( "The plugin «{}» has no argument «{}» in «{}».".format( self.plugin, key, ", ".join( x.name for x in self.__args ) ) )
        else:
            raise TypeError( "type(key) is {}".format( type( key ).__name__ ) )
    
    
    def set( self, provided: ArgsKwargs ) -> None:
        """
        Sets the arguments based on an `ArgsKwargs` collection.
        """
        has_set = set()
        
        if provided.args:
            for index, argument in enumerate( self.__args.keys() ):
                if index >= len( provided.args ):
                    break
                
                try:
                    self.__set_arg( argument, provided.args[index] )
                except Exception as ex:
                    raise ValueError( "Error setting argument «{}» on «{}», see internal error for more details.".format( argument, self.__plugin ) ) from ex
                
                has_set.add( argument )
        
        for argument_name, value in provided.kwargs.items():
            argument = self.__plugin.find_arg( argument_name )
            
            self.__set_arg( argument, value )
            
            if argument in has_set:
                raise ValueError( "Attempt to set the argument «{0}» more than once. Did you pass in the argument both as a keyword and positional parameter?".format( argument ) )
            
            has_set.add( argument )
    
    
    def __set_arg( self, key: PluginArg, value: Optional[object] ):
        if not key in self.__args:
            raise KeyError( "There is no such argument as «{0}» for the «{1}» plugin. The available arguments are: {2}".format( key, self.__plugin.name, ", ".join( str( x ) for x in self.__args.keys() ) ) )
        
        arg = self.__args[key]  # type: PluginArgValue
        
        arg.set_value( value )
    
    
    def incomplete( self ) -> "List[ PluginArgValue ]":
        """
        Returns the set of arguments that require a value to be set before run() is called
        """
        return [x for x in self.__args.values() if not x.is_set]


HFunctionParameterType = MAnnotationFactory( "HFunctionParameterType" )
