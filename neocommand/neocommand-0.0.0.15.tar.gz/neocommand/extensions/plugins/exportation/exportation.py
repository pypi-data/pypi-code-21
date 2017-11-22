"""
Contains function for imports, merges and exports.
"""
from typing import Optional

from intermake import IVisualisable, command, MCMD, VisibilityClass
from mhelper import file_helper, Filename, EFileMode, MOptional
from neocommand.database.endpoints import IEndpoint, IOrigin, MemoryEndpoint
from neocommand.database.entities import iterate_all
from neocommand.helpers.special_types import TNodeLabel, TNodeProperty
from neocommand.helpers.table_draw import Table

LEGACY_EXPORTS = VisibilityClass( name = "legacy_exports", 
                                  default = False, 
                                  comment = "Legacy export functions." )
__LABEL = "@label"
TWriteCsvFilename = Filename[ EFileMode.WRITE, ".csv" ]


@command(visibility = LEGACY_EXPORTS)
def export_update_property( endpoint: IEndpoint, origin:IOrigin, label: TNodeLabel, property: TNodeProperty[ __LABEL ] ):
    """
    Relays a single property from one endpoint to another.
    
    :param endpoint: Where to send the data 
    :param origin: Source set 
    :param label: Label of nodes to update 
    :param property: Property on nodes to update 
    :return: Nothing 
    """
    
    for uid, property_value in MCMD.iterate( origin.origin_get_all_nodes_property( label, property ), "Writing properties" ):
        endpoint.endpoint_create_node( label = label, uid = uid, properties = { property: property_value } )


@command(visibility = LEGACY_EXPORTS)
def export_string(  source: IVisualisable, destination: MOptional[ TWriteCsvFilename ] = None ):
    """
    Exports a Text TXT file from an item, which can be anything.
    
    :param source:          What to export 
    :param destination:     Filename to export. If not specified nothing is written. If extension is missing ".txt" is appended.
    :return                 The text written to the file (or that would be written to the file if `destination` is not specified)
    """
    
    text = str( source )
    
    if destination:
        file_helper.write_all_text( destination, text )
        MCMD.print( "Exported {0} characters to «{1}».".format( len( text ), destination ) )
    
    return text


@command(visibility = LEGACY_EXPORTS)
def export_tables( source: MemoryEndpoint, destination: TWriteCsvFilename ):
    """
    Same as `export_table` for all Tables found in `source`.
     
    :param source: Folder containing tables 
    :param destination: Filename (will be suffixed with the table name) 
    """
    
    for i, x in MCMD.enumerate( iterate_all( source, lambda x: isinstance( x, Table ) ), text = lambda x: x.name, title = "Exporting CSVs" ):  # type: Table
        file_name = file_helper.replace_extension( destination, (x.name or "Table {0}".format( i )) + destination.extension )
        
        # noinspection PyArgumentList
        export_table( MCMD, x, TWriteCsvFilename( file_name ) )


@command(visibility = LEGACY_EXPORTS)
def export_table(  source: Table, destination: TWriteCsvFilename ):
    """
    Exports a CSV file from a Table to a CSV file.
    
    Note: Tables are returned from some plugins. To export a CSV file from the database, use `export_csv`.
    
    :param source: Source table 
    :param destination: Destination file 
    :return: Nothing 
    """
    import csv
    
    with open( destination, "w" ) as file:
        writer = csv.writer( file )
        
        for row in MCMD.iterate( source.rows, "Writing {0}".format( destination.file_name ) ):
            writer.writerow( row )


    
    