from typing import cast
from intermake import EColour, IVisualisable, MENV, ResultsExplorer, UiInfo, constants as mconstants, resources
from neocommand.data.settings import Settings


__author__ = "Martin Rusilowicz"


class Core( IVisualisable ):
    """
    All the data.
    
    See the accessor properties for private field descriptions.
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.__settings = None
        self.__endpoints = None
        self.__results_folder = ResultsExplorer()
    
    
    @property
    def settings( self ):
        if self.__settings is None:
            self.__settings = MENV.local_data.store.get_and_init( "settings", Settings() )
        
        return self.__settings
    
    
    @property
    def endpoint_manager( self ):
        from neocommand.database.endpoint_collections import EndpointManager
        
        if self.__endpoints is None:
            self.__endpoints = EndpointManager()
        
        return cast( EndpointManager, self.__endpoints )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self,
                       comment = "This is the " + MENV.name + " root folder.",
                       type_name = mconstants.VIRTUAL_FOLDER,
                       value = "",
                       colour = EColour.NORMAL,
                       icon = resources.folder,
                       extra_named = (self.__results_folder, self.endpoint_manager, MENV.plugins.plugins()) )
    
    
    def __str__( self ):
        return MENV.abv_name + ":/"


CORE = Core()
"""The core data."""
