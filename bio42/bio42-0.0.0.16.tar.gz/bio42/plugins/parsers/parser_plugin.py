from typing import List, Optional, Union

from intermake import EColour, EThread, IVisualisable, UiInfo, resources as Res
from intermake.engine.environment import MCMD
from intermake.plugins.command_plugin import CommandPlugin
from mhelper import abstract, file_helper, sealed, string_helper
from neocommand.database.endpoints import IEndpoint


__author__ = "Martin Rusilowicz"


class ParserFilter( IVisualisable ):
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.description,
                       type_name = type( self ).__name__,
                       value = ", ".join( self.extension ),
                       colour = EColour.YELLOW,
                       icon = Res.unknown,
                       extra = { "extension":self.extension } )
    
    
    def __init__( self, name: str, extension: Union[ str, List[ str ] ], description: str ):
        self.name = name
        
        if isinstance( extension, str ):
            self.extension = [ extension ]
        else:
            self.extension = extension
        
        self.description = description
    
    
    def __str__( self ):
        return self.name
    
    
    def match( self, file_name ):
        for x in self.extension:
            x = x.lower()
            
            if x.startswith( "." ):
                if file_helper.get_extension( file_name ).lower() == x:
                    return True
            else:
                if file_helper.get_filename( file_name ).lower() == x:
                    return True
        
        return False


class ParserPlugin( CommandPlugin ):
    """
    ABSTRACT

    Base class for parsers.
    Parsers turn files into DbEntity objects

    Derived classes must implement:
        ParserBase.iterate_file

    And may implement:
        ParserBase.clear_caches

    """
    
    
    def visualisable_info( self ) ->UiInfo:
        return super().visualisable_info().supplement(ex_filters = self._filters)
    
    
    def __init__( self, name: str, filters: List[ ParserFilter ], function = None, true_function = None ):
        """
        CONSTRUCTOR
        :param filters: See `ParserFilter`.
        """
        type_name = "Parser ({0} file types)".format( len( filters ) )
        
        super().__init__( names = "Import " + name,
                          description = "Imports: " + ", ".join( "«{}»".format( x ) for x in filters ) + "\n\n" + string_helper.fix_indents( str( type( self ).__doc__ ) ),
                          type_name = type_name,
                          threading = EThread.SINGLE,
                          visibility = None,
                          function = function or self.iterate_file,
                          true_function = true_function,
                          folder = "parsers")
        
        for i, x in enumerate( filters ):
            assert isinstance( x, ParserFilter ), "Must pass a list of classes implementing the <ParserFilter> base class to the parser named «{0}» but item <#{1}> («{2}») is a «{3}».".format( name, i, x, type( x ).__name__ )
        
        self._filters = filters
    
    
    @sealed
    def is_supported( self, file_name: str ) -> bool:
        return self.find_matching_filter( file_name ) is not None
    
    
    @sealed
    def find_matching_filter( self, file_name: str ) -> Optional[ ParserFilter ]:
        """
        Returns the specified file extension handled by this parser.
        Returns None if the extension is not handled by this parser.
        """
        
        for x in self._filters:
            if x.match( file_name ):
                return x
        
        raise ValueError( "Cannot find a filter for «{}». Consider renaming the file.".format( file_name ) )
    
    
    @abstract
    def iterate_file( self, *args, **kwargs ) -> None:
        """
        The implementing class should iterates over a file.
        """
        raise NotImplementedError( "abstract" )
    
    
    @sealed
    def virtual_run( self ) -> Optional[ object ]:
        result = super().virtual_run(  )
        
        for arg in MCMD.args:
            value = arg.value
            
            if isinstance( value, IEndpoint ):
                value.endpoint_flush()
                
                if result is None:
                    result = value
        
        return result
