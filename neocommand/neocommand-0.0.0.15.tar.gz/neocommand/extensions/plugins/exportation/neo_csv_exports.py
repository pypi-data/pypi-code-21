"""
Module containing functions for exporting data "parcels" to Neo4j
"""
import csv
import re
import shutil
from os import path, system
from typing import Callable, List, Optional
from intermake import MCMD, command, m_print_helper
from mhelper import file_helper, string_helper, SwitchError, Filename, EFileMode

from neocommand.data import constants
from neocommand.data.core import CORE
from neocommand.database.entities import Node, Edge
from neocommand.database.endpoints import IOrigin, IEndpoint, NeoCsvFolderEndpoint, DbEndpoint, NULL_ENDPOINT
from neocommand.helpers.neo_csv_helper import NEO_TYPE_COLLECTION, NeoCsvFilename, NeoCsvHeader, NeoType
from neocommand.extensions.plugins.basic import database


IMPORT_DOT_CYPHER = "import.cypher"
IMPORT_DOT_SH = "import.sh"
READ_CYPHER_FILE = Filename[EFileMode.READ, constants.EXT_CYPHER]
READ_SHELL_FILE = Filename[EFileMode.READ, constants.EXT_SH]

__mcmd_folder_name__ = "parcels"


@command()
def parcel_transfer( input: IOrigin, endpoint: IEndpoint ):
    """
    Transfers data from one endpoint to another. 
    :param input:   Source 
    :param endpoint:  Destination 
    :return:        `output` endpoint 
    """
    
    for x in input.origin_get_all():
        if isinstance( x, Node ):
            endpoint.endpoint_create_node( label = x.label, uid = x.uid, properties = x.properties )
        elif isinstance( x, Edge ):
            endpoint.endpoint_create_edge( label = x.label, start_label = x.start.label, start_uid = x.start.uid, end_label = x.end.label, end_uid = x.end.uid, properties = x.properties )
    
    return endpoint


@command()
def parcel_import( endpoint: DbEndpoint, parcel: NeoCsvFolderEndpoint ):
    """
    Runs the import script from the specified parcel.
     
    :param endpoint:  Where to send the data
    :param parcel: NeoCsvFolderEndpoint 
    :return: 
    """
    scr_cypher = path.join( parcel.full_path(), IMPORT_DOT_CYPHER )
    scr_shell = path.join( parcel.full_path(), IMPORT_DOT_SH )
    
    if path.isfile( scr_cypher ):
        if path.isfile( scr_shell ):
            raise ValueError( "Cannot run the import script in this folder because it is ambiguous between «{0}» and «{1}». Either run the file manually or delete one of the scripts.".format( scr_cypher, scr_shell ) )
        
        # noinspection PyTypeChecker
        parcel_run_cypher( endpoint, READ_CYPHER_FILE( scr_cypher ) )
    elif path.isfile( scr_shell ):
        # noinspection PyTypeChecker
        __run_shell( READ_SHELL_FILE( scr_shell ) )
    else:
        raise ValueError( "Cannot run the import script in this folder a script file «{0}» or «{1}» cannot be found. Perhaps you meant to create the script first (see `help_parcels`)".format( scr_cypher, scr_shell ) )


@command()
def parcel_run_cypher( endpoint: DbEndpoint, file: READ_CYPHER_FILE ) -> None:
    """
    Runs a cypher script produced by `neocsv_to_cypher_bulk_script` or `neocsv_to_cypher_add_script`
    
    It breaks the file up into smaller scripts separated by "\n;\n" in order to show progress, but this won't work for files produced outside of these two commands. 
    :param endpoint: Where to send the data (only the directory is used)
    :param file: File to run 
    :return: Nothing
    """
    text = file_helper.read_all_text( file )
    files_needed = re.findall( r'[^"/]*.' + constants.EXT_B42CSV + r'(?=")', text )
    import_folder = endpoint.connection_info.get_import_directory()
    
    if files_needed:
        for file_needed in MCMD.iterate( files_needed, "Transferring files to import folder" ):
            if not import_folder or not path.isdir( import_folder ):
                raise FileNotFoundError( "Cannot prepare files for import because I can't find the Neo4j import folder «{0}». Please define it in settings first.".format( import_folder ) )
            
            # Move file to import directory of Neo4j
            source = path.join( file_helper.get_directory( file ), file_needed )
            dest = path.join( import_folder, file_needed )
            
            if not path.isfile( source ):
                if path.isfile( dest ):
                    if not MCMD.question( "A file noted in the import script («{0}») cannot be found locally («{1}») but appears to exist remotely («{2}»). This may be due to a previously failed import. If you are sure this is the intended file, then we can use recover by using the remote file. If you are unsure, do not continue. Continue?".format( file, source, dest ) ):
                        raise FileNotFoundError( "Cannot prepare files for import because a file noted in the import script («{0}») appears to be missing locally («{1}»). A remote version («{2}») does exist but the user chose to ignore it.".format( file, source, dest ) )
                    else:
                        continue
                else:
                    raise FileNotFoundError( "Cannot prepare files for import because a file noted in the import script («{0}») appears to be missing locally («{1}»). A remote version of this file («{2}») does not exist.".format( file, source, dest ) )
            elif path.isfile( dest ):
                raise FileExistsError( "Cannot prepare files for import a file noted in the import script («{0}») needs to be transferred from the local parcel («{1}») but a file with the same name already exists remotely («{2}»).".format( file, source, dest ) )
            
            shutil.move( source, dest )
    
    scriptlets = text.split( "\n;\n" )
    
    try:
        for scriptlet in MCMD.iterate( scriptlets, "Running commands" ):
            if scriptlet.strip():
                database.cypher( code = scriptlet, output = NULL_ENDPOINT, database = endpoint )
    finally:
        for file_needed in MCMD.iterate( files_needed, "Moving files back from import folder" ):
            source = path.join( file_helper.get_directory( file ), file_needed )
            dest = path.join( import_folder, file_needed )
            shutil.move( dest, source )


def __run_shell( file: str ) -> None:
    """
    Runs a shell script
     
    :param file: File to run 
    :return: Nothing
    """
    MCMD.print( "Passing control to external command. See console output for details." )
    system( file )


# noinspection PyUnusedLocal
@command()
def parcel_db( db_name: str, input: NeoCsvFolderEndpoint, run: bool = True ) -> str:
    """
    Generates and runs an `neo4j-import.exe` script that generates a new database from the parcel.
    
    :param run:                 Run the script after generating it
    :param db_name:              Path to the new database to be created
    :param input:               NeoCsvFolderEndpoint being used - also where the script will be written (see `help parcels`)
    :return:                    Name of resulting script file
    """
    binary_dir = CORE.settings.neo4j_binary_folder
    
    if not binary_dir or not path.isdir( binary_dir ):
        raise m_print_helper.SetupError( "neo4j_binary_folder", binary_dir )
    
    result = []
    result.append( "cd \"{0}\"".format( CORE.settings.neo4j_binary_folder ) )
    script = []
    
    files = __get_files( input )
    
    for file in files:
        if file.is_edge:
            statement = string_helper.strip_lines( __NEW_EDGE )
        else:
            statement = string_helper.strip_lines( __NEW_NODE )
        
        statement = string_helper.bulk_replace( statement, label = file.label, file_name = file.filename )
        script.append( statement )
    
    script_text = " ".join( script )
    
    result.append( "./neo4j-import --into {0} {1} --multiline-fields=true --array-delimiter TAB --skip-bad-relationships=true --skip-duplicate-nodes=true --bad-tolerance=100000000 --ignore-empty-strings=true".format( db_name, script_text ) )
    
    file_name = path.join( input.full_path(), IMPORT_DOT_SH )
    file_helper.write_all_text( file_name, "\n\n".join( result ) )
    
    if run:
        # noinspection PyTypeChecker
        __run_shell( file_name )
    
    return file_name


# noinspection PyUnusedLocal
@command()
def parcel_bulk( input: NeoCsvFolderEndpoint, endpoint: DbEndpoint, run: bool = True ) -> str:
    """
    Generates and runs a Cypher "bulk import" script from a parcel.
    
    :param endpoint:             Database information.
    :param run:                Whether to run the script.
    :param input:              NeoCsvFolderEndpoint being used - also where the script will be written
    :return:                   Name of resulting script file
    """
    result = []
    nc_files = __get_files( input )
    
    for nc_file in nc_files:
        headers, first_line = __get_csv_head( nc_file.filename )
        
        attributes, name_column, start_column, end_column = __create_attribute_script( nc_file, headers, __neo4j_type_to_csv_neo4j_conversion, None )
        
        # Generate the "merge" part of the statement
        if nc_file.is_edge:
            assert name_column is None, "{} {}".format( nc_file.filename, name_column )
            assert start_column is not None, "{} {}".format( nc_file.filename, start_column )
            assert end_column is not None, "{} {}".format( nc_file.filename, end_column )
            
            statement = string_helper.bulk_replace( string_helper.strip_lines( __CSV_EDGE ),
                                                    start_label = nc_file.start_label,
                                                    end_label = nc_file.end_label,
                                                    start_column = headers[start_column],
                                                    end_column = headers[end_column] )
        
        else:
            assert name_column is not None, "{} {}".format( nc_file.filename, name_column )
            assert start_column is None, "{} {}".format( nc_file.filename, start_column )
            assert end_column is None, "{} {}".format( nc_file.filename, end_column )
            
            statement = string_helper.bulk_replace( string_helper.strip_lines( __CSV_NODE ),
                                                    uid = headers[name_column] )
        
        # The filenames are different under UNIX and Windows
        if endpoint.connection_info.get_is_unix():
            file_prefix = constants.PREFIX_UNIX
        else:
            file_prefix = constants.PREFIX_WINDOWS
        
        # The creation method depends on the user's settings and the entity flags
        method = "MERGE"  # now it's always just "Merge", it keeps things simple
        
        statement = string_helper.bulk_replace( statement,
                                                label = nc_file.label,
                                                creation = method,
                                                file_name = file_prefix + nc_file.alone + constants.EXT_B42CSV,
                                                attributes = attributes )
        
        result.append( statement )
    
    file_name = path.join( input.full_path(), IMPORT_DOT_CYPHER )
    file_helper.write_all_text( file_name, "\n\n".join( result ) )
    
    if run:
        # noinspection PyTypeChecker
        parcel_run_cypher( endpoint, file_name )
    
    return file_name


# noinspection PyUnusedLocal
@command()
def parcel_add( input: NeoCsvFolderEndpoint, run: bool = True ) -> str:
    """
    Generates and runs a simple Cypher script from a parcel.
    
    :param run:                Whether to run the script
    :param input:              NeoCsvFolderEndpoint being used - also where the script will be written
    :return:                   Name of resulting script file
    """
    results = []
    files = __get_files( input )
    
    for file in files:
        with open( file.filename, "r" ) as in_file:
            reader = csv.reader( in_file )
            headers = next( reader )
            method = "MERGE"  # Now it's always just "MERGE", it keeps things simple
            
            for row in reader:
                attributes, name_column, start_column, end_column = __create_attribute_script( file, headers, __neo4j_type_to_direct_neo4j_conversion, row )
                
                if file.is_edge:
                    result = string_helper.bulk_replace( string_helper.strip_lines( __ADD_EDGE ),
                                                         start_label = file.start_label,
                                                         start_uid = row[start_column],
                                                         end_label = file.end_label,
                                                         end_uid = row[end_column],
                                                         creation = method,
                                                         label = file.label,
                                                         attributes = attributes )
                else:
                    result = string_helper.bulk_replace( string_helper.strip_lines( __ADD_NODE ),
                                                         creation = method,
                                                         label = file.label,
                                                         uid = row[name_column],
                                                         attributes = attributes )
                
                results.append( result )
    
    file_name = path.join( input.full_path(), IMPORT_DOT_CYPHER )
    file_helper.write_all_text( file_name, "\n\n".join( results ) )
    
    if run:
        # noinspection PyTypeChecker
        parcel_run_cypher( READ_CYPHER_FILE( file_name ) )
    
    return file_name


def __create_attribute_script( filename: NeoCsvFilename, headers, expression: Callable[[NeoCsvFilename, str, int, Optional[List[object]]], Optional[str]], row_data: Optional[List[object]] ):
    """
    Creates the attribute Cypher script given a set of headers and their values.
    """
    name_column = None
    start_column = None
    end_column = None
    attributes = []
    
    for i, header in enumerate( headers ):
        if header.startswith( constants.PRIMARY_KEY_DECORATED_NAME ):
            name_column = i
        elif header.startswith( constants.NEO4J_START_ID_SUFFIX ):
            start_column = i
        elif header.startswith( constants.NEO4J_END_ID_SUFFIX ):
            end_column = i
        else:
            row_value = expression( filename, header, i, row_data )
            
            if row_value is not None:
                attributes.append( row_value )
    
    if attributes:
        attributes = "SET\n" + ",\n".join( attributes )
    else:
        attributes = ""
    
    return attributes, name_column, start_column, end_column


def __get_csv_head( file_name: str ) -> (str, str):
    """
    Gets the CSV headers and the first line of the CSV
    """
    
    with open( file_name, "r" ) as file:
        reader = csv.reader( file )
        try:
            first = next( reader )
            second = next( reader )
            return first, second
        except StopIteration as ex:
            raise ValueError( "Failed to read head from «{}».".format( file_name ) ) from ex


# noinspection PyUnusedLocal
def __neo4j_type_to_csv_neo4j_conversion( nc_file_name: NeoCsvFilename, header_text: str, index: int, row: Optional[List[object]] ) -> Optional[str]:
    """
    Produces the Cypher query that moves from a field `r.X` (which is a string) to `z.X` (which is a T).
    Where field name `X` and field type `T` are defined in the `header_text`.
    """
    nch = NeoCsvHeader.from_decorated_name( nc_file_name, header_text )
    
    value = "r.`{0}`".format( header_text )
    
    if nch.type is NEO_TYPE_COLLECTION.INT.NO_ARRAY:
        result = "toInt({0})".format( value )
    elif nch.type is NEO_TYPE_COLLECTION.FLOAT.NO_ARRAY:
        result = "toFloat({0})".format( value )
    elif nch.type is NEO_TYPE_COLLECTION.STR.NO_ARRAY:
        result = value
    elif nch.type is NEO_TYPE_COLLECTION.BOOL.NO_ARRAY:
        result = "(case {0} when \"True\" then true else false end)".format( value )
    elif nch.type is NEO_TYPE_COLLECTION.STR.ARRAY:
        result = 'split({0},"\\t")'.format( value )
    else:
        raise SwitchError( "nch.type", nch.type )
    
    return "z.`{0}` = {1}".format( nch.name, result )


def __neo4j_type_to_direct_neo4j_conversion( nc_file_name: NeoCsvFilename, header_text: str, index: int, row: Optional[List[str]] ) -> Optional[str]:
    """
    Produces the Cypher query that moves the `value` to a field called `z.X` (which is a `T`).
    Where field name `X` and field type `T` are defined in the `header_text`.
    The value is obtained from `row[index]`.
    """
    if header_text.count( ":" ) != 1:
        raise ValueError( "The column name «{}» isn't a valid NEO4J-style header. The format should be «name:type», but it isn't.".format( header_text ) )
    
    nch = NeoCsvHeader.from_decorated_name( nc_file_name, header_text )
    value = row[index]
    
    
    if nch.type.is_array:
        result = "[{}]".format(",".join(__convert_value(x, nch.type.NO_ARRAY) for x in value.split("\t"))) 
    else:
        result = __convert_value(value, nch.type)
    
    return "z.`{0}` = {1}".format( nch.name, result )
    
def __convert_value( value, nc_type : NeoType ):
    if value is None:
        return None
    
    if nc_type is NEO_TYPE_COLLECTION.INT.NO_ARRAY:
        # noinspection PyTypeChecker
        int( value )  # assertion
        return value
    elif nc_type is NEO_TYPE_COLLECTION.FLOAT.NO_ARRAY:
        # noinspection PyTypeChecker
        float( value )  # assertion
        return value
    elif nc_type is NEO_TYPE_COLLECTION.STR.NO_ARRAY:
        return '"{0}"'.format( str( value ).replace( '"', '\\"' ).replace( "\t", "\\t" ).replace( "\n", "\\n" ) )
    elif nc_type is NEO_TYPE_COLLECTION.BOOL.NO_ARRAY:
        assert value in ("true", "false")
        return value
    else:
        raise SwitchError( "nc_type", nc_type )


def __type_error( header: str, value: Optional[object], type_: type ):
    return "Expected the column with header «{0}» to be of type «{1}» but got a value of type «{2}» (value = «{3}»). This error should never happen because the correct types should have been obtained in the header-type determining step.".format( header, type_.__name__, type( value ).__name__, value )


def __get_files( directory: NeoCsvFolderEndpoint, files: Optional[List[NeoCsvFilename]] = None ) -> List[NeoCsvFilename]:
    """
    Gets files, or if not specified, all files.
    Sorts them nodes-first (because we need to create nodes before edges).
    """
    if files is None:
        files = list( directory.iterate_contents() )
    
    files = list( sorted( files, key = lambda x: x.is_edge ) )
    
    return files


__NEW_EDGE = "--relationships:<label> <file_name>"

__NEW_NODE = "--nodes:<label> <file_name>"

__CSV_NODE = \
    """
    CREATE INDEX ON :<label>(name)
    ;
    
    USING PERIODIC COMMIT
    LOAD CSV WITH HEADERS FROM \"<file_name>\" AS r
    <creation> (z:<label> {uid: r.`<uid>`})
    <attributes>
    ;
    
    """

__CSV_EDGE = \
    """
    USING PERIODIC COMMIT
    LOAD CSV WITH HEADERS FROM \"<file_name>\" AS r
    MATCH (x:<start_label> {uid: r.`<start_column>`})
    MATCH (y:<end_label> {uid: r.`<end_column>`})
    <creation> (x)-[z:<label>]->(y)
    <attributes>
    ;
    
    """

__ADD_NODE = \
    """
    <creation> (z:<label> {uid: "<uid>"})
    <attributes>
    ;
    """

__ADD_EDGE = \
    """
    MATCH (x:<start_label> {uid: "<start_uid>"})
    MATCH (y:<end_label> {uid: "<end_uid>"})
    <creation> (x)-[z:<label>]->(y)
    <attributes>
    ;
    
    """
