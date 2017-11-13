"""
Classes for managing "parcels" - folders that contain a formatted set of entries to be added to the database
"""
from intermake.engine.environment import MENV


__author__ = "Martin Rusilowicz"

from typing import List, cast

from intermake import EColour, IVisualisable, UiInfo, constants as mconstants
from neocommand.database.endpoints import ECHOING_ENDPOINT, NULL_ENDPOINT, IUserIoBase, IMasterOrigin
from neocommand.gui_qt import resources as Res
from mhelper import NotFoundError


class EndpointManager( IVisualisable ):
    """
    Manages pipeline folders
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        See methods of same name for parameter details
        """
        self.__user_endpoints = cast( List[ IUserIoBase ], MENV.local_data.store.get( "user_endpoints", [ ] ) )
        self.__other_endpoints = [ NULL_ENDPOINT, ECHOING_ENDPOINT ]
    
    
    @property
    def user_endpoints( self ) -> List[ IUserIoBase ]:
        return self.__user_endpoints
    
    
    def remove_user_endpoint( self, name: str ):
        for x in self.__user_endpoints:
            if x.endpoint_name == name:
                x.endpoint_deleted()
                self.__user_endpoints.remove( x )
                self.__save_endpoints()
                return
        
        raise NotFoundError( "No user endpoint named «{}».".format( name ) )
    
    
    def __save_endpoints( self ):
        MENV.local_data.store[ "user_endpoints" ] = self.__user_endpoints
    
    
    def add_user_endpoint( self, endpoint: IUserIoBase ):
        for x in self:
            if x.visualisable_info().name == endpoint.endpoint_name:
                raise ValueError( "The name «{}» is already taken.".format( x.endpoint_name ) )
        
        self.__user_endpoints.append( endpoint )
        self.__save_endpoints()
    
    
    def __str__( self ):
        return "Endpoints"
    
    
    def visualisable_info( self ) -> UiInfo:
        x = "{} user and {} inbuilt endpoints".format( len( self.__user_endpoints ), len( self.__other_endpoints ) )
        
        return UiInfo( name = self,
                       comment = "",
                       type_name = mconstants.VIRTUAL_FOLDER,
                       value = x,
                       colour = EColour.YELLOW,
                       icon = Res.folder,
                       extra_named = self.__iter__ )
    
    
    def __iter__( self ):
        yield from self.__other_endpoints
        yield from self.__user_endpoints
        
    def get_database_endpoint(self)-> IMasterOrigin:
        database = None
        
        for ep in self:
            if isinstance(ep, IMasterOrigin):
                if database is not None:
                    raise ValueError("No «database» argument provided to the «cypher» plugin, and I found multiple «DbEndpoint»s that could act as a reasonable default. Perhaps you meant to specify the «database» argument?")
                    
                database = ep
                
        if database is None:
            raise ValueError("No «database» argument provided to the «cypher» plugin, and I could not find any «DbEndpoint» to act as a reasonable default. Perhaps you meant to call «new_connection» first?")
        
        return database
        
