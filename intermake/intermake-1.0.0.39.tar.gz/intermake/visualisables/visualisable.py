from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from flags import Flags
from intermake.hosts.frontends.gui_qt.designer import resources

from mhelper import SwitchError, abstract, exception_helper, override, reflection_helper
from mhelper.qt_helpers.resource_objects import ResourceIcon


class IVisualisable:
    """
    Things visualisable in the GUI.
    """
    
    
    @abstract
    def visualisable_info( self ) -> "UiInfo":
        """
        ABSTRACT
        
        Information for the GUI - see `UiInfo` for more details.
        """
        raise NotImplementedError( "abstract" )


OUBasic = Union[ str, bool, float, int ]
OUAcceptable = Optional[ Union[ str, bool, float, int, List[ OUBasic ], Dict[ str, OUBasic ], Tuple[ OUBasic ], IVisualisable ] ]
#OUExtraIter = Optional[ Union[ Callable[ [ ], Iterable[ OUAcceptable ] ], Iterable[ OUAcceptable ] ] ]
OUExtraIter = Any
# OUExtra = Optional[ Union[ Callable[ [ ], Dict[ str, OUAcceptable ] ], Dict[ str, OUAcceptable ] ] ]
OUExtra = Any


class EColour( Enum ):
    MUTED_FOREGROUND = -2
    NORMAL = -1
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    WHITE = 7


class UiInfoProperty:
    """
    UiInfo meta-data.
    """
    
    
    def __init__( self, key: str, value: object ):
        self.key = key
        self.__value = value
    
    
    def get_value( self ) -> "IVisualisable":
        return as_visualisable( self.get_raw_value() )
    
    
    def get_type( self ) -> type:
        if isinstance( self.__value, IVisualisable ):
            return type( self.__value )
        else:
            return NamedValue
    
    
    def get_raw_type( self ) -> type:
        return type( self.get_raw_value() )
    
    
    def get_raw_value( self ) -> Optional[ object ]:
        return reflection_helper.defunction( self.__value )


class EIterVis( Flags ):
    __no_flags_name__ = "NONE"
    __all_flags_name__ = "ALL"
    BASIC = 1
    PROPERTIES = 2
    CONTENTS = 4


class UiInfo:
    def __init__( self,
                  *,
                  name: str,
                  comment: str,
                  type_name: str,
                  value: str,
                  colour: Optional[ EColour ],
                  icon: Optional[ ResourceIcon ],
                  extra: OUExtra = None,
                  extra_indexed: OUExtraIter = None,
                  extra_named: OUExtraIter = None ):
        """
        Specifies information about an IVisualisable object.
        
        Additional arguments (extra_list and extra) are provided to allow custom information.
        
        * Do not repeat default arguments (e.g. name) in the custom information
        * Extra arguments may be:
            * An IVisualisable
            * A basic type (int, str, float, bool) (providing they are named explicitly via `extra`, or `extra_indexed`)
            * A list providing any of the above
            * A callable providing any of the above 
        
        :param name:            Name of the object.
        :param comment:         Comment on the object.
        :param type_name:       Name of the object type.
        :param value:           Value of the object.
        :param colour:          Colour of the object.
        :param icon:            Icon of the object.
        :param extra:           Extra properties. This dict can yield any `object`s. The properties are named after the `dict.keys`.
        :param extra_named:     Extra properties. This iterable must only yield `IVisualisable`s. The properties are named after the `IVisualisable.visualisable_info().name`.
        :param extra_indexed:   Extra properties. This iterable can yield any `object`s. The properties are named after the order in which they appear. 
        """
        self.name = name
        self.comment = comment
        self.type_name = type_name
        self.value = value
        self.colour = colour if (colour is not None) else EColour.NORMAL
        self.icon = icon
        self.extra = extra
        self.extra_named = extra_named
        self.extra_indexed = extra_indexed
    
    
    def iter_children( self, iter: EIterVis = EIterVis.ALL ) -> Iterator[ UiInfoProperty ]:
        """
        Iterates the children of this `UiInfo`, yielding `NamedValue`s.
        """
        try:
            if iter.BASIC:
                yield UiInfoProperty( "name", str( self.name ) )
                yield UiInfoProperty( "comment", str( self.comment ) )
            
            if iter.PROPERTIES:
                meta_dict = reflection_helper.defunction( self.extra )
                
                if meta_dict is not None:
                    for key, value in meta_dict.items():
                        value = reflection_helper.defunction( value )
                        yield UiInfoProperty( key, value )
            
            if iter.CONTENTS:
                meta_named = reflection_helper.defunction( self.extra_named )
                
                if meta_named is not None:
                    for value in meta_named:
                        exception_helper.assert_type( "value", value, IVisualisable )
                        
                        yield UiInfoProperty( str( value.visualisable_info().name ), value )
                
                meta_iter = reflection_helper.defunction( self.extra_indexed )
                
                if meta_iter is not None:
                    for index, item in enumerate( meta_iter ):
                        yield UiInfoProperty( "{}".format( index ), item )
        except Exception as ex:
            raise ValueError( "Problem iterating children of {}. See causing error for details.".format( self ) ) from ex
    
    
    def supplement( self, **kwargs ):
        """
        Fluent interface that updates `self.extra`.
        """
        self.extra.update( kwargs )
        return self
    
    
    def __str__( self ):
        return "«{0}» = «{1}» ({2})".format( self.name, self.value, self.type_name )
    
    
    def ccolour( self ) -> Tuple[ str, str ]:
        """
        Console colour
        :return: Tuple (FG, BG) 
        """
        from colorama import Back, Fore
        
        c = self.colour
        if c == EColour.RED:
            return Fore.RED, Back.RED
        elif c == EColour.GREEN:
            return Fore.GREEN, Back.GREEN
        elif c == EColour.BLUE:
            return Fore.BLUE, Back.BLUE
        elif c == EColour.CYAN:
            return Fore.CYAN, Back.CYAN
        elif c == EColour.MAGENTA:
            return Fore.MAGENTA, Back.MAGENTA
        elif c == EColour.YELLOW:
            return Fore.YELLOW, Back.YELLOW
        elif c == EColour.BLACK:
            return Fore.BLACK, Back.BLACK
        elif c == EColour.WHITE:
            return Fore.WHITE, Back.WHITE
        elif c == EColour.NORMAL:
            return Fore.RESET, Back.RESET
        elif c == EColour.MUTED_FOREGROUND:
            return Fore.LIGHTBLACK_EX, Back.LIGHTBLACK_EX
        else:
            raise SwitchError( "c", c )
    
    
    def qcolour( self ):
        """
        QT Colour
        :rtype: QColor
        """
        from PyQt5.QtGui import QColor
        from PyQt5.QtCore import Qt
        
        c = self.colour
        if c == EColour.RED:
            return QColor( Qt.darkRed )
        elif c == EColour.GREEN:
            return QColor( Qt.darkGreen )
        elif c == EColour.BLUE:
            return QColor( Qt.darkBlue )
        elif c == EColour.CYAN:
            return QColor( Qt.darkCyan )
        elif c == EColour.MAGENTA:
            return QColor( Qt.darkMagenta )
        elif c == EColour.YELLOW:
            return QColor( Qt.darkYellow )
        elif c == EColour.BLACK:
            return QColor( Qt.black )
        elif c == EColour.WHITE:
            return QColor( Qt.darkYellow )
        elif c == EColour.NORMAL:
            return QColor( Qt.black )
        elif c == EColour.MUTED_FOREGROUND:
            return QColor( Qt.gray )
        else:
            raise SwitchError( "c", c )


def as_visualisable( x ) -> IVisualisable:
    """
    Obtains the object `x` as an `IVisualisable`, putting it in a wrapper if necessary.
    """
    if isinstance( x, IVisualisable ):
        return x
    
    return NamedValue( "", x )


class NamedValue( IVisualisable ):
    """
    Used to convert basic types to an IVisualisable.
    """
    
    
    def __init__( self, name, value ):
        """
        CONSTRUCTOR
        :param name:        Name and key of the value 
        :param value:       Underlying value 
        """
        if isinstance( value, IVisualisable ):
            raise TypeError( "`IVisualisable` «{}» provided to NamedValue (name = «{}»). This is probably a mistake.".format( name, value ) )
        
        self.name = name
        self.value = value
        self.__icon = None
        self.__colour = None
        self.__type_name = None
        self.__comment = None
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        if self.__icon is None:
            self.__type_name = "{}".format( type( self.value ).__name__ )
            
            if self.value is None:
                self.__icon = resources.failure
                self.__colour = EColour.MUTED_FOREGROUND
            
            elif isinstance( self.value, int ):
                self.__icon = resources.integer
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, float ):
                self.__icon = resources.integer
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, list ) or isinstance( self.value, tuple ) or isinstance( self.value, dict ):
                self.__icon = resources.list
                self.__colour = EColour.MAGENTA if len( self.value ) else EColour.MUTED_FOREGROUND
            elif isinstance( self.value, str ):
                self.__icon = resources.string
                self.__colour = EColour.MAGENTA
            elif isinstance( self.value, bool ):
                self.__icon = resources.success if self.value else resources.failure
                self.__colour = EColour.MAGENTA
            else:
                self.__icon = resources.unknown
                self.__colour = EColour.MAGENTA
                self.__type_name = "internal"
                self.__comment = "Internal type: {}".format( type( self.value ) )
        
        result = UiInfo( name = self.name,
                         comment = self.__comment,
                         type_name = self.__type_name,
                         value = str( self ),
                         colour = self.__colour,
                         icon = self.__icon )
        
        if isinstance( self.value, list ) or isinstance( self.value, tuple ):
            result.extra_indexed = self.value
        
        if isinstance( self.value, dict ):
            result.extra = self.value
        
        return result
    
    
    def __str__( self ):
        if isinstance( self.value, list ) or isinstance( self.value, tuple ) or isinstance( self.value, dict ):
            l = len( self.value )
            
            if l == 0:
                return "(no items)"
            else:
                return "({} items)".format( len( self.value ) )
        else:
            return str( self.value )
