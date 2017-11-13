from typing import Optional
from intermake import MCMD, MENV, PathToVisualisable, command, console_explorer, visibilities
from mhelper import Dirname, Filename, MOptional, MUnion, Password, file_helper

from neocommand.data import constants
from neocommand.data.core import CORE
from neocommand.data.settings import ENeo4jDriver
from neocommand.database.endpoints import DbEndpoint, GexfEndpoint, IEndpoint, IIoBase, IMasterOrigin, IOrigin, NeoCsvFolderEndpoint
from neocommand.extensions.plugins.basic import endpoints_utils
from neocommand.helpers.special_types import TEndpointName


@command( highlight = True )
def new_gephi( name: Optional[str] = None, path: MOptional[Filename] = None ) -> IIoBase:
    """
    Creates a new endpoint: Gephi
    
    At least the `name` or `path` argument must be specified.
    
    :param name:    Name of the endpoint.
                    If not specified, the path will be used.
    :param path:    Path to GEXF file.
                    This will be created if it doesn't already exist.
                    If not specified, a file in the `workspace` will be created with the specified `name`.
    :return: The endpoint is returned. 
    """
    name, path = __resolve_name_and_path( name, path, ".gexf" )
    endpoint = GexfEndpoint( name, path )
    CORE.endpoint_manager.add_user_endpoint( endpoint )
    return endpoint


@command( highlight = True )
def new_parcel( name: Optional[str] = None, path: MOptional[Dirname] = None ) -> IIoBase:
    """
    Creates a new endpoint: CSV-folder
    
    (These endpoints are folders containing CSV files in the correct format for bulk importing into the database)
    
    At least the `name` or `path` argument must be specified.
    
    :param name:    Name of the endpoint.
                    If not specified, the path will be used.
    :param path:    Path to folder.
                    This will be created if it doesn't already exist.
                    If not specified, a folder in the `workspace` will be created with the specified `name`.
    :return: The endpoint is returned. 
    """
    name, path = __resolve_name_and_path( name, path, "" )
    endpoint = NeoCsvFolderEndpoint( name, path )
    CORE.endpoint_manager.add_user_endpoint( endpoint )
    
    if len( endpoint ) == 0:
        MCMD.information( "New parcel created at «{}».".format( endpoint.full_path() ) )
    else:
        MCMD.information( "Existing parcel opened at «{}».".format( endpoint.full_path() ) )
    
    return endpoint


@command( highlight = True )
def new_connection( name: str, driver: ENeo4jDriver, host: str, user: str, password: Password, directory: MOptional[Dirname] = None, unix: Optional[bool] = None, windows: Optional[bool] = None, port: str = "7474", plain = False ) -> IIoBase:
    """
    Creates a new endpoint: Neo4j database
    
    :param windows:     Set if the database is hosted on Windows. Optional.
    :param unix:        Set if the database is hosted on Unix. Optional.
    :param directory:   Set to the local Neo4j installation directory. Optional.
    :param name:        Name you will call the endpoint
    :param driver:      Database driver 
    :param host:        Database host
    :param user:        Database username
    :param password:    Database password. Nb. Use `password=prompt` to be prompted by the CLI.
    :param port:        Database port 
    :param plain:       Normally, passwords will be stored on the system keyring (requires the `keyring` Python package) and are not displayed to the user. If this flag is set, the password is stored in plain text and is not masked by the UI.
    :return:            The endpoint is returned.  
    """
    if windows and unix:
        raise ValueError( "Cannot specify both the `windows` and `unix` parameters." )
    
    unix = not windows
    
    endpoint = DbEndpoint( name = name,
                           driver = driver,
                           remote_address = host,
                           user_name = user,
                           password = password.value,
                           directory = str( directory ) if directory else None,
                           is_unix = unix,
                           port = port,
                           keyring = not plain )
    
    CORE.endpoint_manager.add_user_endpoint( endpoint )
    return endpoint


def __resolve_name_and_path( name: Optional[str], path: MOptional[MUnion[Filename, Dirname]], extension : str ):
    if name is None:
        if path is None:
            raise ValueError( "A name or path must be specified." )
        
        name = file_helper.get_filename_without_extension( path )
    
    if path is None:
        path = file_helper.join( MENV.local_data.get_workspace(), constants.FOLDER_PIPELINES, name ) + extension
    
    return name, path


@command()
def connections() -> None:
    """
    Lists the endpoints.
    """
    console_explorer.re_ls( PathToVisualisable.find_path( CORE, CORE.endpoint_manager ) )


@command()
def close( name: TEndpointName ):
    """
    Removes a reference to a user-endpoint.
    (This affects $(APPNAME) only - contents on disk, if any, are unaffected)
    
    :param name: Name of the endpoint to remove.
    """
    CORE.endpoint_manager.remove_user_endpoint( name )
    MCMD.information( "Endpoint closed: {}".format( name ) )
    MCMD.information( "(Note that closing endpoints does not remove them from disk)" )


@command()
def transfer( input: IOrigin, output: IEndpoint, lookup: Optional[IMasterOrigin] = False, cache: Optional[bool] = None ):
    """
    Transfers information from one endpoint to another.
     
    :param input:   Input, where to source data from.
    :param output:  Output, where to send data to.
    :param lookup:  Optional parameter. Lookup all entities in `input` here to acquire the latest version. 
    :param cache:   When `lookup` is set, permits in-memory caching of lookups. Disable only if the data doesn't fit in memory. The default is `True`. 
    """
    if lookup is None:
        if cache is not None:
            raise ValueError( "Cannot specify `cache` parameter when `lookup` is empty." )
        
        for entity in input.origin_get_all():
            output.endpoint_add_entity( entity )
    else:
        if cache is None:
            cache = True
        
        for entity in endpoints_utils.transfer_with_lookup( input, lookup, cache ):
            output.endpoint_add_entity( entity )


@command( visibility = visibilities.TEST )
def small_test( endpoint: IEndpoint ):
    """
    Tests the endpoint
    :param endpoint:    Endpoint to send to 
    """
    endpoint.endpoint_create_node( label = "node_label", uid = "start_node_uid", properties = { "prop1": 1, "prop2": 2 } )
    endpoint.endpoint_create_node( label = "node_label", uid = "end_node_uid", properties = { "prop1": 1, "prop2": 2 } )
    endpoint.endpoint_create_edge( label = "edge_label", start_label = "node_label", start_uid = "start_node_uid", end_label = "node_label", end_uid = "end_node_uid", properties = { "prop1": 1, "prop2": 2 } )
    folder = endpoint.endpoint_create_folder( "folder" )
    folder.endpoint_create_node( label = "node_label", uid = "start_node_uid_2", properties = { "prop1": 1, "prop2": 2 } )
    folder.endpoint_create_node( label = "node_label", uid = "end_node_uid_2", properties = { "prop1": 1, "prop2": 2 } )
    folder.endpoint_create_edge( label = "edge_label", start_label = "node_label", start_uid = "start_node_uid_2", end_label = "node_label", end_uid = "end_node_uid_2", properties = { "prop1": 1, "prop2": 2 } )
