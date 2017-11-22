"""
Functions for applying annotations from the Uniprot online service.
"""
from typing import Optional

from intermake.engine.environment import MCMD
from mhelper import BatchList, SwitchError, MFlags
from neocommand.helpers.special_types import TNodeProperty

from intermake import command

from bio42 import constants
from neocommand.database.endpoints import IEndpoint, IOrigin
from bio42.helpers import bio42b_helper


@command()
def find_accessions( endpoint: IEndpoint,
                     origin: IOrigin,
                     input_accession: str,
                     output_accession: str = "ACC",
                     input_property: TNodeProperty[ constants.NODE_SEQUENCE ] = "uid",
                     input_column: Optional[ int ] = None,
                     output_property: TNodeProperty[ constants.NODE_SEQUENCE ] = "uniprot",
                     batch_size: int = 100 ):
    """
    Adds accessions to sequences.
    
    :param endpoint:            Where to send the updates to
    :param origin:              Nodes to update
    :param input_accession:     Type of the input accession. See http://www.uniprot.org/help/programmatic_access#id_mapping_examples
    :param output_accession:    Type of the output accession.
    :param input_property:      Property to retrieve the input accession from. 
    :param input_column:        Column of the input accession (for pipe-delimited `input_property`s of the form `a|b|c`) 
    :param output_property:     Property to store the output accession into.
    :param batch_size:          Number of requests to make to Uniprot at once. 
    :return:                    `endpoint` 
    """
    from urllib.parse import urlencode
    from urllib.request import Request
    from urllib.request import urlopen
    
    SEQUENCE_LABEL = constants.NODE_SEQUENCE
    URL = "http://www.uniprot.org/uploadlists/"
    
    to_do = origin.origin_get_all_nodes_property( SEQUENCE_LABEL, input_property )
    to_do = BatchList( to_do, batch_size )
    
    with MCMD.action( "Processing sequences", len( to_do ) ) as action:
        for next_portion in to_do:
            action.increment( len( next_portion ) )
            
            next_dict = { }
            
            for sequence_uid, property_value in next_portion:
                if input_column is not None:
                    property_value = property_value.split( "|" )[ input_column ]
                
                next_dict[ property_value ] = sequence_uid
            
            data = urlencode( {
                "from"  : input_accession,
                "to"    : output_accession,
                "format": "tab",
                "query" : " ".join( next_dict.keys() )
            } )
            
            data = data.encode( 'ascii' )
            
            request = Request( URL, data )
            
            response = urlopen( request )
            tsv = response.read( 200000 ).decode( "utf-8" )
            
            lines = tsv.split( "\n" )[ 1: ]  # first line just says "From-To"
            
            for line in lines:
                accession_from, accession_to = line.split( "\t", 1 )
                sequence_uid = next_dict[ accession_from ]  # type: str
                
                endpoint.endpoint_create_node( label = SEQUENCE_LABEL, uid = sequence_uid, properties = { output_property: accession_to } )
    
    endpoint.endpoint_flush()
    
    return endpoint


class EAutoAnnotateMode( MFlags ):
    KEGG = 1
    GO = 2
    PFAM = 3


@command()
def auto_annotate( endpoint: IEndpoint,
                   origin: IOrigin,
                   accession_property: str = "uniprot",
                   batch_size: int = 100,
                   create_edges: bool = True,
                   create_properties: bool = False,
                   create_nodes: bool = True,
                   property_prefix: str = "uniprot_",
                   modes: Optional[ EAutoAnnotateMode ] = None ):
    """
    Annotates sequences using Uniprot.
    Supports: PFAM, GO, KEGG.
    
    :param modes:                   What to apply. If not specified defaults to everything.
    :param create_properties:       Create properties for metadata. 
    :param create_edges:            Create edges for metadata.
    :param create_nodes:            Create nodes for metadata (requires `create_edges`).
    :param endpoint:                Where to send the results to
    :param origin:                  Where to get the sequences from
    :param accession_property:      Property to get the Uniprot accession from (on the `origin` sequences)
    :param batch_size:              Number of sequences to process at once. Note that Uniprot may also impose its own batching.
    :param property_prefix:         Prefix to add to the resultant properties (added to the `origin` sequences)
    :return:                        The `endpoint` argument.
    """
    import uniprot
    
    SEQUENCE_LABEL = constants.NODE_SEQUENCE
    to_do = origin.origin_get_all_nodes_property( SEQUENCE_LABEL, accession_property )
    to_do = BatchList( to_do, batch_size )
    
    interesting = [ ]
    
    if modes is None:
        modes = EAutoAnnotateMode.PFAM | EAutoAnnotateMode.GO | EAutoAnnotateMode.KEGG
    
    # noinspection PyTypeChecker
    for mode in modes:
        if mode.GO:
            interesting.append( ("go", constants.NODE_GOCLASS, bio42b_helper.go_id_to_uid) )
        elif mode.PFAM:
            interesting.append( ("pfam", constants.NODE_PFAMCLASS, bio42b_helper.pfam_id_to_uid) )
        elif mode.KEGG:
            interesting.append( ("kegg", constants.NODE_KEGGCLASS, bio42b_helper.kegg_id_to_uid) )
        else:
            raise SwitchError( "modes[n]", mode )
    
    with MCMD.action( "Iterating sequences", len( to_do ) ) as action:
        for batch in to_do:
            action.increment( len( batch ) )
            accession_to_uid = dict( (v, k) for k, v in batch )
            
            sequence_id_string = " ".join( [ x[ 1 ] for x in batch ] )
            uniprot_data = uniprot.batch_uniprot_metadata( sequence_id_string, 'cache' )
            
            assert uniprot_data
            
            for sequence_accession, sequence_metadata in uniprot_data.items():
                sequence_uid = accession_to_uid[ sequence_accession ]
                
                new_dict = { }
                
                for attribute, class_, uid_mapping in interesting:
                    if attribute in sequence_metadata:
                        value = sequence_metadata[ attribute ]
                        value = [ x.split( ";", 1 )[ 0 ].strip() for x in value ]
                        new_dict[ property_prefix + attribute ] = value
                        
                        if create_edges:
                            for mode in value:
                                x_uid = uid_mapping( mode )
                                
                                if create_nodes:
                                    endpoint.endpoint_create_node( label = class_, uid = x_uid, properties = { } )
                                
                                endpoint.endpoint_create_edge( label = constants.EDGE_GOCLASS_CONTAINS_SEQUENCE, start_label = class_, start_uid = x_uid, end_label = SEQUENCE_LABEL, end_uid = sequence_uid, properties = { } )
                
                if create_properties:
                    endpoint.endpoint_create_node( label = SEQUENCE_LABEL, uid = sequence_uid, properties = new_dict )
    
    return endpoint
