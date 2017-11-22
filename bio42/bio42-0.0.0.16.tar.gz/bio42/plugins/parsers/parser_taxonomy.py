"""
Imports taxa

Normally the taxa are downloaded as a set of DMP files, these will need to be renamed so we can tell the difference between them
Specifically we want NODES.DMP and NAMES.DMP
"""
from os import path
from typing import Dict
from typing import List

from intermake import MCMD, command, MENV
from mhelper import file_helper, Filename, EFileMode, MOptional
from neocommand import IEndpoint, constants

from bio42 import constants
from bio42.plugins.parsers.parser_plugin import ParserPlugin, ParserFilter


__author__ = "Martin Rusilowicz"
__mcmd_folder_name__ = "parsers"


def _str_to_bool( text: str ) -> bool:
    """
    Converts the text to a boolean value.
    """
    if text == "0":
        return False
    elif text == "1":
        return True
    else:
        raise ValueError( "Cannot convert text \"" + text + "\" to bool." )


_EXT_DMP = ".dmp"

@command()
class ParserTaxonomy( ParserPlugin ):
    """
    Reads the taxonomy database, published by NCBI, producing Taxon nodes, as well as edges between them, denoting the taxonomic hierarchy.
    """
    
    
    def __init__( self ):
        super().__init__( "Taxonomy", [ ParserFilter( "nodes", "nodes.dmp", "NCBI Nodes file" ) ] )
        # noinspection PyUnresolvedReferences
    
    
    def iterate_file( self,
                      endpoint: IEndpoint,
                      file_name: MOptional[ Filename[ EFileMode.READ, _EXT_DMP ] ],
                      names_file_name: MOptional[ Filename[ EFileMode.READ, _EXT_DMP ] ] ) -> None:
        """
        
        :param endpoint:            Where to send the parsed data to. 
        :param file_name:           Where to get the data from. 
        :param names_file_name:     Names file. If left blank assumes a file called `names.dmp` in the same directory as the nodes file. 
        :return: 
        """
        # Unfortunately its not enough just to load the Nodes taxa file, we also need the Names
        
        
        if not names_file_name:
            tax_file_names = [ file_helper.replace_filename( file_name, "names.dmp" ), file_helper.replace_extension( file_name, ".names" ) ]
            for possibility in tax_file_names:
                if path.isfile( possibility ):
                    names_file_name = possibility
                    break
        
        MCMD.print( "Reading taxonomy from «{}» and «{}».".format( file_name, names_file_name ) )
        
        tax_names = _read_names( names_file_name )
        
        # Always create an unknown
        _create_unknown_taxon_node( endpoint )
        
        with MCMD.action( "Iterating nodes" ) as action:
            with open( file_name, "r" ) as file:
                for line in file:
                    action.increment()
                    self.yield_line( endpoint, line, tax_names )
    
    
    @staticmethod
    def yield_line( endpoint: IEndpoint, line: str, tax_names: Dict[ int, Dict[ str, List[ str ] ] ] ) -> None:
        # 00 tax_id                            -- node id in GenBank taxonomy database
        # 01 parent tax_id                     -- parent node id in GenBank taxonomy database
        # 02 rank                              -- rank of this node (superkingdom, kingdom, ...)
        # 03 embl code#                        -- locus-name prefix; not unique
        # 04 division id                       -- see division.dmp file
        # 05 inherited div flag  (1 or 0)      -- 1 if node inherits division from parent
        # 06 genetic code id                   -- see gencode.dmp file
        # 07 inherited GC  flag  (1 or 0)      -- 1 if node inherits genetic code from parent
        # 08 mitochondrial genetic code id     -- see gencode.dmp file
        # 09 inherited MGC flag  (1 or 0)      -- 1 if node inherits mitochondrial gencode from parent
        # 10 GenBank hidden flag (1 or 0)      -- 1 if  name is suppressed in GenBank entry lineage
        # 11 hidden subtree root flag (1 or 0) -- 1 if this subtree has no sequence data yet
        # 12 comments                          -- free-text comments and citations
        
        fields = [ x.strip( " \t|\n" ) for x in line.split( "\t|\t" ) ]
        
        if len( fields ) != 13:
            raise ValueError( "This is not a taxonomy node database." )
        
        # super( ).__init__( fields[ 0 ] )
        
        name = fields[ 0 ]
        my_id = int( fields[ 0 ] )
        applicable_names = tax_names[ my_id ]
        
        # Each value of applicable_names is
        # 00 id
        # 01 name
        # 02 unique name
        # 03 class
        if "scientific_name" in applicable_names:
            scientific_name = applicable_names[ "scientific_name" ][ 0 ]
        else:
            scientific_name = None
        
        parent_id = int( fields[ 1 ] )
        
        props = {
            "parent_id"                    : parent_id,
            "rank"                         : fields[ 2 ],  # don't short-code this any more since its reasonably useful
            "embl_code"                    : fields[ 3 ],  # letters
            "division_id"                  : int( fields[ 4 ] ),
            "inherited_div_flag"           : _str_to_bool( fields[ 5 ] ),
            "genetic_code_id"              : int( fields[ 6 ] ),
            "inherited_gc_flag"            : _str_to_bool( fields[ 7 ] ),
            "mitochondrial_genetic_code_id": int( fields[ 8 ] ),
            "inherited_mgc_flag"           : _str_to_bool( fields[ 9 ] ),
            "genbank_hidden_flag"          : _str_to_bool( fields[ 10 ] ),
            "hidden_subtree_root_flag"     : _str_to_bool( fields[ 11 ] ),
            "comments"                     : fields[ 12 ],
            "acronym"                      : read_name( applicable_names, "acronym" ),
            "anamorph"                     : read_name( applicable_names, "anamorph" ),
            "authority"                    : read_name( applicable_names, "authority" ),
            "blast_name"                   : read_name( applicable_names, "blast_name" ),
            "common_name"                  : read_name( applicable_names, "common_name" ),
            "equivalent_name"              : read_name( applicable_names, "equivalent_name" ),
            "genbank_acronym"              : read_name( applicable_names, "genbank_acronym" ),
            "genbank_anamorph"             : read_name( applicable_names, "genbank_anamorph" ),
            "genbank_common_name"          : read_name( applicable_names, "genbank_common_name" ),
            "genbank_synonym"              : read_name( applicable_names, "genbank_synonym" ),
            "in_part"                      : read_name( applicable_names, "in_part" ),
            "includes"                     : read_name( applicable_names, "includes" ),
            "misnomer"                     : read_name( applicable_names, "misnomer" ),
            "misspelling"                  : read_name( applicable_names, "misspelling" ),
            "scientific_name"              : scientific_name,
            "scientific_names"             : read_name( applicable_names, "scientific_name" ),
            "synonym"                      : read_name( applicable_names, "synonym" ),
            "teleomorph"                   : read_name( applicable_names, "teleomorph" ),
            "type_material"                : read_name( applicable_names, "type_material" ) }
        
        endpoint.endpoint_create_node( label = constants.NODE_TAXON, uid = name, properties = props )
        endpoint.endpoint_create_edge( label = constants.EDGE_TAXON_CONTAINS_TAXON, start_label = constants.NODE_TAXON, start_uid = str( parent_id ), end_label = constants.NODE_TAXON, end_uid = name, properties = { } )
        

parser_taxonomy = ParserTaxonomy.instance

def read_name( dictionary, type_ ):
    if type_ not in dictionary:
        return ""
    
    names = dictionary[ type_ ]
    
    return ", ".join( names )


def _create_unknown_taxon_node( endpoint: IEndpoint ) -> None:
    props = {
        "parent_id"                    : -1,
        "rank"                         : "",
        "embl_code"                    : "",
        "division_id"                  : -1,
        "inherited_div_flag"           : False,
        "genetic_code_id"              : -1,
        "inherited_gc_flag"            : False,
        "mitochondrial_genetic_code_id": -1,
        "inherited_mgc_flag"           : False,
        "genbank_hidden_flag"          : False,
        "hidden_subtree_root_flag"     : False,
        "comments"                     : "Unknown signifier automatically generated by " + MENV.name + " " + MENV.version,
        "acronym"                      : "",
        "anamorph"                     : "",
        "authority"                    : "",
        "blast_name"                   : "",
        "common_name"                  : "unknown",
        "equivalent_name"              : "",
        "genbank_acronym"              : "",
        "genbank_anamorph"             : "",
        "genbank_common_name"          : "",
        "genbank_synonym"              : "",
        "in_part"                      : "",
        "includes"                     : "",
        "misnomer"                     : "",
        "misspelling"                  : "",
        "scientific_name"              : "unknown",
        "synonym"                      : "",
        "teleomorph"                   : "",
        "type_material"                : "" }
    
    endpoint.endpoint_create_node( label = constants.NODE_TAXON, uid = constants.UID_TAXON_UNKNOWN, properties = props )


def _read_names( file_name ):
    """
    Reads a taxonomy names file.
    :param file_name: File to read 
    :return: Dictionary:
                K: Taxon ID
                V: Dictionary:
                    K: Name type (e.g. "scientific_name")
                    V: LIST:
                        V: Name
    """
    assert file_name, "A taxonomy names file must be specified."
    
    result_names = { }  # type: Dict[ int, Dict[ str, List[ str ] ] ]
    
    with MCMD.action( "Reading names" ) as action:
        with open( file_name, "r" ) as file:
            for line in file:
                action.increment()
                fields = [ x.strip( " \t|\n" ) for x in line.split( "\t|\t" ) ]
                id = int( fields[ 0 ] )
                
                name = fields[ 1 ]
                name_type = fields[ 3 ].replace( " ", "_" ).replace( "-", "_" )
                
                if id in result_names:
                    dict_for_id = result_names[ id ]
                else:
                    dict_for_id = { }
                    result_names[ id ] = dict_for_id
                
                if name_type in dict_for_id:
                    names_for_class = dict_for_id[ name_type ]
                else:
                    names_for_class = [ ]
                    dict_for_id[ name_type ] = names_for_class
                
                names_for_class.append( name )
    
    return result_names


def _read_scientific_names( file_name ):
    names = _read_names( file_name )
    result = { }
    
    for k, v in names.items():
        scientific_names = v.get( "scientific_name" )
        
        if scientific_names:
            scientific_name = scientific_names[ 0 ]
            result[ k ] = scientific_name
    
    return result




