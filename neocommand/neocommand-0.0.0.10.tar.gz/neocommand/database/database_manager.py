"""
Connecting to the database, executing queries, and conversion of results.
"""
from threading import Thread
from time import sleep, time
from typing import Dict, Optional, cast

import neo4j.v1
import py2neo

from intermake import AsyncResult
from intermake.engine.constants import mandated
from intermake.engine.environment import MCMD
from intermake.visualisables.visualisable import IVisualisable, UiInfo, EColour
from mhelper import SwitchError, override
from neocommand.data import constants
from neocommand.data.settings import ENeo4jDriver
from neocommand.database.endpoints import IEndpoint, MemoryEndpoint
from neocommand.database.entities import Edge, Node
from neocommand.gui_qt import resources

__author__ = "Martin Rusilowicz"


class DbStats( IVisualisable ):
    """
    Simple type - statistics on a query
    """
    __props = ("relationships_deleted", "constraints_added", "nodes_created", "labels_added", "nodes_deleted", "constraints_removed", "relationships_created", "indexes_removed", "indexes_added", "labels_removed", "properties_set", "relationships_deleted")
    
    
    def __init__( self, cypher, dictionary: Dict[ str, object ] ):
        self.cypher = cypher
        self.relationships_deleted = dictionary.get( "relationships_deleted", 0 )
        self.constraints_added = dictionary.get( "constraints_added", 0 )
        self.contains_updates = dictionary.get( "contains_updates", False )
        self.nodes_created = dictionary.get( "nodes_created", 0 )
        self.labels_added = dictionary.get( "labels_added", 0 )
        self.nodes_deleted = dictionary.get( "nodes_deleted", 0 )
        self.constraints_removed = dictionary.get( "constraints_removed", 0 )
        self.relationships_created = dictionary.get( "relationships_created", 0 )
        self.indexes_removed = dictionary.get( "indexes_removed", 0 )
        self.indexes_added = dictionary.get( "indexes_added", 0 )
        self.labels_removed = dictionary.get( "labels_removed", 0 )
        self.properties_set = dictionary.get( "properties_set", 0 )
        self.relationships_deleted = dictionary.get( "relationships_deleted", 0 )
    
    
    def __str__( self ):
        ss = [ ]
        
        for prop in self.__props:
            if self.__dict__[ prop ]:
                ss.append( "{} {}".format( self.__dict__[ prop ], prop ) )
                
        if not ss:
            return "No changes"
        
        return ", ".join( ss )
    
    
    def as_dict( self ):
        return dict( (x, y) for x, y in self.__dict__.items() if x in self.__props )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = "stats",
                       comment = self.cypher,
                       type_name = "stats",
                       value = str( self ),
                       colour = EColour.BLUE,
                       icon = resources.script,
                       extra = self.as_dict )


class IDbDriverSession:
    def run( self, cypher: str, parameters: dict, output: IEndpoint ) -> DbStats:
        raise NotImplementedError( "abstract" )


class DbManager:
    """
    Connects to the Neo4j database and executes queries
    """
    
    _count = 0
    """Index of instance"""
    
    __neo4j_v1_driver_object = None
    """The driver in use"""
    
    __connection_mash = None
    """Something we use to identify the connection parameters"""
    
    
    def __init__( self, driver: ENeo4jDriver, remote_address: str, user_name: str, password: str, remote_port: str ):
        """
        CONSTRUCTOR
        """
        DbManager._count += 1
        
        self.__index = self._count
        self.__cached_session = cast( IDbDriverSession, None )
        self.driver = driver
        self.remote_address = remote_address
        self.remote_port = remote_port
        self.user_name = user_name
        self.password = password
    
    
    @mandated
    def run_cypher( self,
                    title: str,
                    cypher: str,
                    output: IEndpoint,
                    parameters: Dict[ str, object ] = None,
                    time_out: float = 604800,
                    retry_count: int = 9999 ) -> DbStats:
        """
        Runs a cypher procedure
        
        :param title: Title (for progress indicator) 
        :param cypher: Procedure text  
        :param parameters: Parameters on the procedure
        :param time_out: Timeout, in seconds 
        :param retry_count: How many times to retry 
        :param output: Where to send any output
        :return: Results dependent on results_mode.
        """
        
        session = self.__session()
        
        if parameters is None:
            parameters = { }
        
        
        def __thread_function():
            try:
                return session.run( cypher, parameters, output )
            except Exception as ex:
                ss = [ ]
                ss.append( "Query failed:\n" )
                ss.append( "[EXCEPTION]\n" )
                ss.append( str( ex ) )
                ss.append( "\n\n" )
                ss.append( "[CYPHER]\n" )
                ss.append( cypher )
                ss.append( "\n\n" )
                ss.append( "[PARAMETERS]\n" )
                ss.append( "\n".join( "{}={}".format( k, v ) for k, v in parameters.items() ) )
                ss.append( "\n" )
                raise ValueError( "".join( ss ) ) from ex
        
        
        while True:
            worker_thread = DbManager.__FnThread( __thread_function )
            worker_thread.start()
            start_time = time()
            
            worker_thread.join( 5 )
            
            if worker_thread.result is None:
                # No result after 5 seconds - show that we are still busy
                with MCMD.action( "Cypher: " + title ) as a:
                    while True:
                        worker_thread.join( 2 )  # 5 seconds is too long for iTerm to recognise that we are still alive, creating a somewhat irritating flickering timer icon. Use 2 seconds instead.
                        a.still_alive()
                        
                        if worker_thread.result is not None:
                            break
                        
                        if time_out:
                            elapsed_time = time() - start_time
                            
                            if elapsed_time > time_out:
                                break
            
            if time_out:
                if worker_thread.result is None:
                    # Timed out - our timer - no result was stored
                    try_again = True
                elif isinstance( worker_thread.result.exception, TimeoutError ):
                    # Timed out - Neo4j/HTTP timer - someone probably pulled out the network cable halfway through :(
                    try_again = True
                else:
                    # Some other error - fail
                    try_again = False
            else:
                # No timeout set - fail for anything (even a Neo4j timeout - we'll raise it as an exception further down
                try_again = False
            
            if try_again:
                # Timed out
                # - Drop the session, it's dead :(
                self.__cached_session = None
                retry_timer = 60
                retry_count -= 1
                
                if retry_count < 0:
                    MCMD.warning( "Query timed out after {0} seconds. No retries remaining.".format( time_out ) )
                    raise TimeoutError( "Database access timed out after {0} seconds. Please check that you are connected to the database. If you didn't expect this message you may wish to simplify your query or increase the timeout period. The query text follows: ".format( time_out ) + cypher )
                
                MCMD.warning( "Query timed out after {0} seconds. {1} retries remaining, retrying in {2} seconds".format( time_out, retry_count, retry_timer ) )
                
                with MCMD.action( "Query timed out, retrying shortly", retry_timer ) as action:
                    for i in range( 0, retry_timer ):
                        action.increment()
                        sleep( 1 )
            else:
                break
        
        worker_thread.result.raise_exception()
        
        return worker_thread.result.result
    
    
    def __is_connected( self ) -> bool:
        """
        Are we connected to the database?
        :return: 
        """
        return self.__cached_session is not None
    
    
    @override
    def __str__( self ):
        """
        String representation
        """
        return "Db#{0}( connection = {1} \)".format( self.__index, "Established" if self.__is_connected() else "Pending" )
    
    
    class __FnThread( Thread ):
        def __init__( self, fn ):
            """
            CONSTRUCTOR
            Simple function-as-thread
            """
            super().__init__()
            self._fn = fn
            self.result = None  # type: Optional[AsyncResult]
        
        
        def run( self ):
            self.result = AsyncResult.construct( self._fn )
            assert self.result is not None
    
    
    def __session( self ) -> IDbDriverSession:
        """
        Obtains the active database session, connecting to the database if required
        Raises on failure
        """
        if self.__cached_session:
            return self.__cached_session
        elif self.driver == ENeo4jDriver.PY2NEO:
            self.__cached_session = Py2neoSession( self )
        elif self.driver == ENeo4jDriver.NEO4JV1:
            self.__cached_session = Neo4jv1Session( self )
        else:
            raise SwitchError( "settings.neo4j_driver", self.driver )
        
        # Assert the connection
        ep = MemoryEndpoint()
        self.__cached_session.run( "RETURN 1", { }, ep )
        check = ep.contents[ 0 ]
        
        if check != 1:
            raise ConnectionError( "Unexpected result from server «{0}» «{1}».".format( type( check ).__name__, check ) )
        
        return self.__cached_session


class Py2neoSession( IDbDriverSession ):
    """
    PY2NEO DRIVER
    """
    
    
    def __init__( self, db: DbManager ):
        self.driver = py2neo.Graph( "http://" + db.remote_address + ":" + db.remote_port, user = db.user_name, password = db.password, bolt = False )
        
        if not self.driver:
            raise ConnectionError( "Failed to obtain connection to server (no error returned)." )
        
        py2neo.http.socket_timeout = 604800  # 1 week in seconds
    
    
    def run( self, cypher: str, parameters: dict, output: IEndpoint ) -> DbStats:
        cursor = self.driver.run( cypher, parameters )
        
        try:
            self._convert_py2neo_entity( cursor, output )
            return DbStats( cypher, cursor.stats().__dict__ )
        finally:
            cursor.close()
    
    
    def _convert_py2neo_entity( self, entity: object, output: IEndpoint ) -> None:
        """
        Converts an arbitrary root_object to an `IEntity`.
        See the `docket_from_` methods to see what types are handled.
         
        :param entity:   Thing to convert 
        :return:         A `Docket` or `MemoryEndpoint` instance 
        """
        if isinstance( entity, py2neo.Cursor ):
            self._convert_py2neo_cursor( entity, output )
        elif isinstance( entity, py2neo.Node ):
            self._convert_py2neo_node( entity, output )
        elif isinstance( entity, py2neo.Relationship ):
            self._convert_py2neo_edge( entity, output )
        elif isinstance( entity, py2neo.Path ):
            self._convert_py2neo_path( entity, output )
        else:
            output.endpoint_add_data( entity )
    
    
    def _convert_py2neo_cursor( self, cursor: py2neo.Cursor, output: IEndpoint ):
        for record in cursor:
            for entity in record:
                self._convert_py2neo_entity( entity, output )
    
    
    def _convert_py2neo_path( self, p: neo4j.v1.Path, output: IEndpoint ) -> None:
        folder = output.endpoint_create_folder( "path" )
        
        for x in p:
            self._convert_py2neo_entity( x, folder )
    
    
    def _convert_py2neo_node( self, node: py2neo.Node, output: IEndpoint ) -> None:
        output.endpoint_add_node( self._convert_py2neo_node_creator( node ) )
    
    
    def _convert_py2neo_edge( self, edge: py2neo.Relationship, output: IEndpoint ) -> None:
        start = self._convert_py2neo_node_creator( edge.start_node() )
        end = self._convert_py2neo_node_creator( edge.end_node() )
        edge_ = Edge( label = edge.types()[ 0 ], start = start, end = end, data = dict( edge ) )
        output.endpoint_add_edge( edge_ )
    
    
    @staticmethod
    def _convert_py2neo_node_creator( node: py2neo.Node ) -> py2neo.Node:
        """
        Converts a Node to a Docket.
        """
        if len( node.labels() ) != 1:
            raise ValueError( "Convert node to docket expected 1 label but {0} were received: {1}".format( len( node.labels() ), ", ".join( node.labels() ) ) )
        
        uid = node[ constants.PROP_ALL_PRIMARY_KEY ]
        
        if not uid:
            raise ValueError( "Convert node to docket expected a UID but the UID is empty." )
        
        label = "".join( str( x ) for x in node.labels() )
        
        return Node( label = label, uid = uid, iid = None, properties = dict( node ) )


class Neo4jv1Session( IDbDriverSession ):
    """
    NEO4J DRIVER
    """
    __neo4j_v1_driver_object = None
    
    
    def __init__( self, db: DbManager ):
        cls = type( self )
        
        if cls.__neo4j_v1_driver_object is None:
            url = "bolt://" + db.remote_address + ":7687"
            auth = neo4j.v1.basic_auth( db.user_name, db.password )
            cls.__neo4j_v1_driver_object = neo4j.v1.GraphDatabase.driver( url, auth = auth )
        else:
            url = None
        
        try:
            self.driver = cls.__neo4j_v1_driver_object.session()
        except Exception as ex:
            raise ConnectionError( "Failed to connect to the database using the following connection: URL = «{0}», auth = «{1}», password = «{2}». The error returned is «{3}»".format( url, db.user_name, "*****" if db.password else "[MISSING]", ex ) )
    
    
    def run( self, cypher: str, parameters: dict, output: IEndpoint ) -> DbStats:
        cursor = self.driver.run( cypher, parameters )
        self._convert_neo4j_entity( cursor, output )
        return DbStats( cypher, cursor.consume().counters.__dict__ )
    
    
    def _convert_neo4j_entity( self, entity: object, output: IEndpoint ) -> None:
        if isinstance( entity, neo4j.v1.StatementResult ):
            self._convert_neo4j_cursor( entity, output )
        elif isinstance( entity, neo4j.v1.Node ):
            self._convert_neo4j_node( entity, output )
        elif isinstance( entity, neo4j.v1.Relationship ):
            self.convert_neo4j_edge( entity, output )
        elif isinstance( entity, neo4j.v1.Path ):
            self._convert_neo4j_path( entity, output )
        else:
            output.endpoint_add_data( entity )
    
    
    def _convert_neo4j_cursor( self, cursor: neo4j.v1.StatementResult, output: IEndpoint ):
        for record in cursor:
            for _, entity in record.items():
                self._convert_neo4j_entity( entity, output )
    
    
    def _convert_neo4j_path( self, p: py2neo.Path, output: IEndpoint ) -> None:
        folder = output.endpoint_create_folder( "path" )
        
        for x in p:
            self._convert_neo4j_entity( x, folder )
    
    
    @staticmethod
    def _convert_neo4j_node( node: neo4j.v1.Node, output: IEndpoint ) -> None:
        """
        Converts a Node to a Docket.
        """
        if len( node.labels ) != 1:
            raise ValueError( "Convert node to docket expected 1 label but {0} were received: {1}".format( len( node.labels() ), ", ".join( node.labels() ) ) )
        
        uid = node[ constants.PROP_ALL_PRIMARY_KEY ]
        
        if not uid:
            raise ValueError( "Convert node to docket expected a UID but the UID is empty." )
        
        label = "".join( str( x ) for x in node.labels )
        
        output.endpoint_create_node( label = label, uid = uid, properties = dict( node ) )
    
    
    @staticmethod
    def convert_neo4j_edge( edge: neo4j.v1.Relationship, output: IEndpoint ) -> None:
        start = Node( iid = edge.start )
        end = Node( iid = edge.end )
        edge_ = Edge( label = edge.type, iid = edge.id, start = start, end = end, data = dict( edge ) )
        output.endpoint_add_edge( edge_ )
