import csv
from typing import List, Optional


from intermake.engine.environment import MCMD
from mhelper import string_helper as StringHelper, Filename, EFileMode
from neocommand.helpers.special_types import TEdgeLabel, TNodeLabel

from intermake import command

from neocommand.database.endpoints import IEndpoint


__mcmd_folder_name__ = "parsers"
TReadCsvFilename = Filename[ EFileMode.READ, ".csv" ]

@command()
def import_csv( file                    : TReadCsvFilename,
                endpoint                : IEndpoint,
                tsv                     : bool = False,
                edge_label              : TEdgeLabel = None,
                start_node_label        : TNodeLabel = None,
                start_node_uid_column   : str = None,
                start_node_properties   : Optional[List[str]] = None,
                end_node_properties     : Optional[List[str]] = None,
                edge_properties         : Optional[List[str]] = None,
                end_node_label          : TNodeLabel = None,
                end_node_uid_column     : str = None,
                create_end_nodes        : bool = False,
                create_start_nodes      : bool = False,
                create_edges            : bool = False ):
    """
    Creates nodes and/or edges from a CSV file.
     
        NODE(key_label, *key_uid_column)   <--   edge_label   <--- NODE(value_label, *value_uid_column)
        
    Edges and nodes are not created with any properties.
    
    :param tsv:                      Import as TSV rather than CSV.
    
    :param file:                     CSV source file 
    :param endpoint:                 Where things get sent
    
    :param create_end_nodes:         Whether to create the end nodes 
    
    :param create_edges:             Whether to create the edges between the nodes
    :param edge_label:               Label of the edges.
    :param edge_properties:          Columns (names or indices) identifying edge properties.
    
    :param create_start_nodes:       Whether to create the start nodes
    :param start_node_label:         Label of the start nodes
    :param start_node_uid_column:    Column (name or index) identifying the start nodes' UIDs
    :param start_node_properties:    Columns (names or indices) identifying start-node properties.
    
    :param end_node_label:           Label of the end nodes
    :param end_node_uid_column:      Column (name or index) identifying the end nodes' UIDs.
    :param end_node_properties:      Columns (names or indices) identifying end-node properties.
    
    
    :return: IEndpoint 
    """
    # Check arguments
    if create_edges:
        if not edge_label:
            raise ValueError("`edge_label` is mandatory when `create_edges` is set.")
    else:
        if edge_label or edge_properties:
            raise ValueError("`edge_label` and `edge_properties` are prohibited when `create_edges` is not set.")
        
    if not create_start_nodes and start_node_properties:
        raise ValueError("`start_node_properties` is prohibited when `create_start_nodes` is not set.")
    
    if not create_end_nodes and end_node_properties:
        raise ValueError("`end_node_properties` is prohibited when `create_end_nodes` is not set.")
        
    if create_start_nodes or create_edges:
        if not start_node_label or not start_node_uid_column:
            raise ValueError("`start_node_label` and `start_node_uid_column` are mandatory when either `create_start_nodes` or `create_edges` are not set.")
    else:
        if start_node_label or start_node_uid_column:
            raise ValueError("`start_node_label` and `start_node_uid_column` are prohibited when neither `create_start_nodes` nor `create_edges` are set.")

    if create_end_nodes or create_edges:
        if not end_node_label or not end_node_uid_column:
            raise ValueError("`end_node_label` and `end_node_uid_column` are mandatory when either `create_end_nodes` or `create_edges` are not set.")
    else:
        if end_node_label or end_node_uid_column:
            raise ValueError("`end_node_label` and `end_node_uid_column` are prohibited when neither `create_end_nodes` nor `create_edges` are set.")
        
    end_node_properties_2 = end_node_properties or []          #type: List[str]
    start_node_properties_2 = start_node_properties or []      #type: List[str]
    edge_properties_2 = edge_properties or []                  #type: List[str]
    
    with MCMD.action( "Reading CSV data" ) as action:
        with open( str( file ) ) as csv_file:
            if tsv:
                reader = csv.reader( csv_file, dialect = csv.excel_tab )
            else:
                reader = csv.reader( csv_file )
            
            headers = next( reader )
            
            end_node_property_indices = __get_indices( end_node_properties_2, headers )
            start_node_property_indices = __get_indices( start_node_properties_2, headers )
            edge_property_indices = __get_indices( edge_properties_2, headers )
            
            if end_node_uid_column is not None:
                try:
                    end_node_uid_column_index = StringHelper.name_index( headers, end_node_uid_column )
                except Exception as ex:
                    raise ValueError( "Failed to find `end_node_uid_column`" ) from ex
            else:
                end_node_uid_column_index = None
            
            if start_node_uid_column is not None:
                try:
                    start_node_uid_column_index = StringHelper.name_index( headers, start_node_uid_column )
                except Exception as ex:
                    raise ValueError( "Failed to find `start_node_uid_column_index`" ) from ex
            else:
                start_node_uid_column_index = None
            
            for row in MCMD.iterate( reader, "Reading file" ):
                action.increment()
                
                if create_end_nodes or create_edges:
                    end_node_uid = row[ end_node_uid_column_index ]
                    
                if create_start_nodes or create_edges:
                    start_node_uid = row[ start_node_uid_column_index ]
                
                if create_end_nodes:
                    props = __read_properties(row, end_node_properties_2, end_node_property_indices)
                    endpoint.endpoint_create_node( label = end_node_label, uid = end_node_uid, properties = props )
                
                if create_start_nodes:
                    props = __read_properties(row, start_node_properties_2, start_node_property_indices)
                    endpoint.endpoint_create_node( label = start_node_label, uid = start_node_uid, properties = props )
                
                if create_edges:
                    props = __read_properties(row, edge_properties_2, edge_property_indices)
                    endpoint.endpoint_create_edge( label = edge_label, start_label = start_node_label, start_uid = start_node_uid, end_label = end_node_label, end_uid = end_node_uid, properties = props )
                    
    endpoint.endpoint_flush()
    
    return endpoint


def __get_indices( names, headers ):
    for name in names:
        if name not in headers:
            raise LookupError("The specified name «{}» is not in the headers: «{}»".format(name, headers))
    
    return [ headers.index( x ) for x in names ]


def __read_properties( row, end_node_properties, end_node_property_indices ):
    return dict((name, row[end_node_property_indices[index]]) for index, name in enumerate(end_node_properties))
