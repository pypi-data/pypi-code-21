"""
The set of core $(APP_NAME) commands.

Use `cmdlist` to obtain the list of most commonly used commands.
"""
import os
import re
from os import path
from typing import Optional

from colorama import Style

from intermake import cli_helper, command, visibilities
from intermake.engine.environment import MCMD
from mhelper import file_helper
from neocommand.data import constants
from neocommand.data.core import CORE
from neocommand.database.endpoints import DbEndpoint, ECHOING_ENDPOINT, IEndpoint, NULL_ENDPOINT
from neocommand.helpers import database_helper
from neocommand.helpers.table_draw import Table
from neocommand.extensions.plugin_classes.script import Script, HScriptParam, ScriptPlugin


__author__ = "Martin Rusilowicz"


@command( visibility = visibilities.ADVANCED )
def set_database( endpoint: DbEndpoint, new_value: Optional[ str ] = None, restart: bool = False ):
    """
    Displays and optionally changes the neo4j database.
    
    :param endpoint: Database to modify 
    :param new_value: OPTIONAL. New database to use. Leave blank for unchanged.
    :param restart: Restart neo4j in order to move to the new database.
    """
    file_name = path.join( CORE.settings.neo4j_binary_folder, "../conf/neo4j.conf" )
    text = file_helper.read_all_text( file_name )
    
    PATTERN = "dbms\.active_database=.*"
    
    rx = re.search( PATTERN, text )
    
    MCMD.print( rx.group( 0 ) )
    MCMD.print( "CURRENT VALUE: " + rx.group( 0 ).split( "=", 1 )[ 1 ] )
    
    if new_value:
        text = re.sub( PATTERN, "dbms.active_database=" + new_value, text, 1 )
        
        file_helper.recycle_file( file_name )
        file_helper.write_all_text( file_name, text )
        
        MCMD.print( "NEW VALUE: " + new_value )
    
    if restart:
        neo4j( endpoint = endpoint, command = "restart" )


@command( visibility = visibilities.ADVANCED )
def neo4j( endpoint: DbEndpoint, command: Optional[ str ] = "" ):
    """
    Starts or stops neo4j

    :param endpoint: Database to control
    :param command: The command to issue to Neo4j, typically `start`, `status` or `stop`
    """
    os.system( path.join( endpoint.connection_info.get_binary_directory(), "neo4j" ) + " " + command )


@command()
def save_script( file_name: str, script: ScriptPlugin ):
    """
    Saves a ScriptPlugin's script to a file
    
    :param file_name: Where to save the file. Defaults to ".cypher" extension. 
    :param script: Script to save
    """
    
    file_name = file_helper.default_extension( file_name, ".cypher" )
    
    file_helper.write_all_text( file_name, script.create( None, True ) )
    
    MCMD.information( cli_helper.format_kv( "Written file", file_name ) )


@command()
def cypher( code: str, output: Optional[IEndpoint ] = None, database: Optional[DbEndpoint ] = None ):
    """
    Runs some Cypher code
    
    NOTE: From the CLI you can use the much abbreviated `=` command to run a cypher query.
          Otherwise you will have to be careful with special symbols (' ', '=', '"') in your code, which have meaning to the CLI.
    
    :param database:    Database to run code on. This parameter can be ignored if you only have one database-connected endpoint.
    :param output:      Where to send the result to. If not specified the result is sent to the echoing endpoint (`/endpoints/echo`). 
    :param code:        The code to run
    """
    if output is None:
        output = ECHOING_ENDPOINT
        
    return Script( cypher = code,
                   name = "User script",
                   description = "User script" )( database = database, output = output )


__CREATE_CONSTRAINT = Script( cypher = """CREATE CONSTRAINT ON (node:<LABEL>) ASSERT node.<PROPERTY> IS UNIQUE""",
                              arguments = { "label"   : HScriptParam[ str],
                                            "property": [HScriptParam[ str], constants.PROP_ALL_PRIMARY_KEY] } )


@command()
def optimise( database: DbEndpoint ):
    """
    Ensure the database is running smoothly. 
    :param database: Endpoint to optimise
    """
    
    with MCMD.action( "Obtaining labels" ):
        labels = database_helper.node_labels( database )
    
    messages = Table()
    
    for label in MCMD.iterate( labels, "Processing", text = True ):
        try:
            __CREATE_CONSTRAINT( label = label,
                                 database = database,
                                 output = NULL_ENDPOINT )
            messages.add_row( label, "OK" )
        except Exception as ex:
            messages.add_row( label, str( ex ) )
    
    MCMD.print( messages.to_string() )
    
    MCMD.print( "Note: Indexes may take some time to generate. Use the " + constants.COL_CMD + ":schema" + Style.RESET_ALL + " command from within the Neo4j browser to obtain the current status." )
