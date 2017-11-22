import re
from collections import defaultdict
from typing import List, Optional, Tuple, Union, Dict, Iterator, cast
from uuid import uuid4

import datetime
from Bio import SeqIO
from Bio.Alphabet import Alphabet
from Bio.SeqFeature import CompoundLocation, FeatureLocation, Reference, SeqFeature
from Bio.SeqRecord import SeqRecord

import intermake
from intermake import command, MCMD
from intermake.plugins.command_plugin import help_command
from mhelper import Filename, EFileMode, file_helper, array_helper, SwitchError, string_helper
from neocommand import IEndpoint, NEO_TYPE_COLLECTION, CountingEndpointWrapper

from bio42 import constants
from bio42.plugins.parsers.parser_plugin import ParserPlugin, ParserFilter
from bio42.plugins.parsers import parser_taxonomy


__author__ = "Martin Rusilowicz"
__mcmd_folder_name__ = "parsers"

ULocation = Union[ FeatureLocation, int, List[ FeatureLocation ], List[ int ] ]
"""
Union of types that can be used to identify a location within a sequence.
"""


class LocationExtract:
    def __init__( self, locations: ULocation ):
        if type( locations ) is not list:
            locations = [ locations ]
        
        start = [ ]
        end = [ ]
        
        # noinspection PyTypeChecker
        for location in locations:
            if type( location ) is int:
                start.append( location )
                end.append( location )
            elif type( location ) in [ FeatureLocation, CompoundLocation ]:
                start.append( location.start )
                end.append( location.end )
            else:
                raise SwitchError( "location", location )
        
        self.start, self.start_type = self.__translate_location( start )
        self.end, self.end_type = self.__translate_location( end )
    
    
    @staticmethod
    def __translate_location( positions ) -> Tuple[ List[ int ], List[ str ] ]:
        indices = [ ]
        types = [ ]
        
        for i, v in enumerate( positions ):
            if isinstance( v, int ):  # BioPython positions inherit int
                types.append( type( v ).__name__ )
                indices.append( int( v ) )
            else:
                raise ValueError( "Don't know how to convert the location value «{0}» of type «{1}»".format( v, type( v ) ) )
        
        return indices, types


@command()
class ParserSequence( ParserPlugin ):
    """
    Parses sequence files from a variety of BioPython supported formats (requires BioPython), creating Sequence nodes.
    
    A large amount of supplementary information is added to the nodes, including all available properties, Reference and Feature nodes, as well as the edges to them.
    
    Resultant meta-graph:
    
    Nodes:
        'SOURCE'      (when `source` argument specified)
        'SEQUENCE'    (actual label determined by `record` argument)
        'FEATURE'     (actual label dependent on feature)
        'REFERENCE'
        
    Edges:
        'SOURCE' -CONTAINS- 'SEQUENCE'
        'SEQUENCE' -CONTAINS- 'FEATURE'
        'SEQUENCE' -CONTAINS- 'REFERENCE'
        'TAXON' -CONTAINS- 'SEQUENCE'       (dependent on `edges` and `taxa` parameters)
        'ELEMENT' -CONTAINS- 'SEQUENCE'     (dependent on `edges` parameter, 'ELEMENT' label determined by `edges` parameter)
        
    Properties:
        Many properties are dynamic and dependent on the information found in the source file.
        These variable annotation properties are given a `_` prefix.
        'SEQUENCE' and 'FEATURE' nodes are given a `sequence` property, dependent on the `no_seq` parameter.
    """
    
    
    class ParserFilter( ParserFilter ):
        def __init__( self, name: str, code: str, extension: Union[ str, List[ str ] ], description: str, detect_records: Optional[ str ] = None ):
            """
            :param name: Inherited 
            :param code: BioPython parser code 
            :param extension: Inherited 
            :param description: Inherited 
            """
            super().__init__( name, extension, description )
            self.detect_records = detect_records
            self.code = code
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        extensions = [ ]
        
        extensions.append( self.ParserFilter( "ABIF", "abif", ".abif", "Applied Biosystem's sequencing trace format" ) )
        extensions.append( self.ParserFilter( "ACE", "ace", ".ace", "Reads the contig. sequences from an ACE assembly file." ) )
        extensions.append( self.ParserFilter( "EMBL", "embl", ".embl", "The EMBL flat file format." ) )
        extensions.append( self.ParserFilter( "FASTA", "fasta", ".fasta", "The generic sequence file format where each record starts with an identifier line starting with a \">\" character, followed by lines of sequence.", detect_records = ">.*" ) )
        extensions.append( self.ParserFilter( "FASTQ", "fastq", ".fastq", "A \"FASTA like\" format used by Sanger which also stores PHRED sequence quality values (with an ASCII offset of 33)." ) )
        extensions.append( self.ParserFilter( "FASTQ (Sanger)", "fastq-sanger", ".fastq-sanger", "An alias for \"fastq\" for consistency with BioPerl and EMBOSS" ) )
        extensions.append( self.ParserFilter( "FASTQ (Solexa)", "fastq-solexa", ".fastq-solexa", "Original Solexa/Illumnia variant of the FASTQ format which encodes Solexa quality scores (not PHRED quality scores) with an ASCII offset of 64." ) )
        extensions.append( self.ParserFilter( "FASTQ (Illumina)", "fastq-illumina", ".fastq-illumina", "Solexa/Illumina 1.3 to 1.7 variant of the FASTQ format which encodes PHRED quality scores with an ASCII offset of 64 (not 33). Note as of version 1.8 of the CASAVA pipeline Illumina will produce FASTQ files using the standard Sanger encoding." ) )
        extensions.append( self.ParserFilter( "Genbank", "genbank", [ ".genbank", ".gbff", ".gb" ], "The GenBank or GenPept flat file format.", detect_records = "//.*" ) )
        extensions.append( self.ParserFilter( "IntelliGenetics", "ig", ".ig", "The IntelliGenetics file format, apparently the same as the MASE alignment format." ) )
        extensions.append( self.ParserFilter( "IMGT", "imgt", ".imgt", "An EMBL like format from IMGT where the feature tables are more indented to allow for longer feature types." ) )
        extensions.append( self.ParserFilter( "Protein Data Bank", "pdb-seqres", ".pdb-seqres", "Reads a Protein Data Bank (PDB) file to determine the complete protein sequence as it appears in the header (no dependencies)." ) )
        extensions.append( self.ParserFilter( "Bio.PDB", "pdb-atom", ".pdb-atom", "Uses Bio.PDB to determine the (partial) protein sequence as it appears in the structure based on the atom coordinate section of the file (requires NumPy for Bio.PDB)." ) )
        extensions.append( self.ParserFilter( "PHRED-output", "phd", ".phd", "Output from PHRED, used by PHRAP and CONSED for input." ) )
        extensions.append( self.ParserFilter( "NBRF", "pir", ".pir", "A \"FASTA like\" format introduced by the National Biomedical Research Foundation (NBRF) for the Protein Information Resource (PIR) database, now part of UniProt." ) )
        extensions.append( self.ParserFilter( "XML (SeqXML)", "seqxml", ".seqxml", "SeqXML, simple XML format described in Schmitt et al (2011)." ) )
        extensions.append( self.ParserFilter( "SFF", "sff", ".sff", "Standard Flowgram Format (SFF), typical output from Roche 454." ) )
        extensions.append( self.ParserFilter( "SFF (trimmed)", "sff-trim", ".sff-trim", "Standard Flowgram Format (SFF) with given trimming applied." ) )
        extensions.append( self.ParserFilter( "XML (UniProt)", "swiss", ".swiss", "Plain text Swiss-Prot aka UniProt format." ) )
        extensions.append( self.ParserFilter( "TSV", "tab", [ ".tab", ".tsv" ], "Simple two column tab separated sequence files, where each line holds a record's identifier and sequence. For example , this is used as by Aligent's eArray software when saving microarray probes in a minimal tab delimited text file." ) )
        extensions.append( self.ParserFilter( "Quality", "qual", ".qual", "A \"FASTA like\" format holding PHRED quality values from sequencing DNA, but no actual sequences (usually provided in separate FASTA files)." ) )
        extensions.append( self.ParserFilter( "TXT (UniProt)", "uniprot-xml", ".uniprot-xml", "The UniProt XML format (replacement for the SwissProt plain text format which we call \"swiss\")" ) )
        
        super().__init__( "Sequences", extensions, function = self.__Proc.__init__, true_function = self.iterate_file )
    
    
    # noinspection PyTypeChecker
    def iterate_file( self, *args, **kwargs ):
        if "_owner" in kwargs:
            del kwargs[ "_owner" ]
        
        self.__Proc( _owner = self, *args, **kwargs )
    
    
    class __Proc:
        # noinspection SpellCheckingInspection
        def __init__( self,
                      file: Filename[ EFileMode.READ ],
                      endpoint: IEndpoint,
                      include_source: bool = False,
                      include_record_sequence: bool = False,
                      include_feature_sequence: bool = False,
                      include_references: bool = False,
                      include_features: bool = True,
                      include_qualifiers: bool = True,
                      include_annotations: bool = True,
                      id_parts: Optional[ List[ str ] ] = None,
                      user_edges: Optional[ List[ str ] ] = None,
                      taxonomy_file: Optional[ List[ str ] ] = None,
                      record_label: str = "Record",
                      biopython_extraction: bool = False,
                      no_count: bool = False,
                      _owner: Optional[ object ] = None ):
            """
            :param no_count:                  No counting.
                                              When set, skips the record counting step (this step is only used to estimate the processing time).
            :param endpoint:                  Endpoint.
                                              Where to send the parsed data.
            :param file:                      Input file.
                                              The file to read
            :param biopython_extraction:      BioPython-extract.
                                              When set uses BioPython's extract feature. When `False` uses a custom quick method (faster but less reliable).
            :param record_label:                     Record label.
                                              The type of the records in the file. This has a general default, but could be something more specific: `Genome`, `Gene`, `Cds`, etc.
            :param user_edges:                Edge list. See `user_edges_help`.
            :param include_record_sequence:                      Record sequences.
                                              When set, full sequence data is added to the created Record nodes.
            :param include_feature_sequence:                      Feature sequences.
                                              When set, full sequence data is added to the created Feature nodes.
            :param taxonomy_file:                      Taxonomy-names file.
                                              Required for the special case noted for the `edges` argument, otherwise unused.
            :param include_source:                    Source edges.
                                              When set, an edge to the 'Source' node is included, denoting the origin of the data (i.e. the file path).
                                              This may be useful in limited circumstances when combining multiple datasets into the same
                                              database, but incurs an additional memory overhead of one additional edge per sequence.
            :param id_parts:                  ID Parts. See `id_parts_help`.
                                              If no argument is specified, all parts are discarded and the entirety used as the UID.
            :param include_features:          Create nodes for features.
            :param include_references:        Create nodes for references.
            :param include_annotations:       Create properties for record annotations. 
            :param include_qualifiers:        Create properties for feature annotations ("qualifiers").
            :param _owner:                    Internal parameter; do not modify.
            """
            
            self.include_record_sequence = include_record_sequence
            self.include_feature_sequence = include_feature_sequence
            self.include_references = include_references
            self.include_features = include_features
            self.include_annotations = include_annotations
            self.include_qualifiers = include_qualifiers
            self.taxonomy_names_list = parser_taxonomy._read_scientific_names( taxonomy_file ) if taxonomy_file else None
            self.id_parts = id_parts
            self.id_part_has_uid = constants.PROP_ALL_PRIMARY_KEY in id_parts if id_parts else False
            self.endpoint = CountingEndpointWrapper( endpoint )
            self.create_edges = self.__parse_user_edges_argument( user_edges )
            self.record_label = record_label
            
            _owner = cast( ParserSequence, _owner )
            
            handler = _owner.find_matching_filter( file )  # type: ParserSequence.ParserFilter
            
            if include_source:
                self.source_uid = str( uuid4() )
                endpoint.endpoint_create_node( label = constants.NODE_SOURCE,
                                               uid = self.source_uid,
                                               properties = { "file_name"  : str( file ),
                                                              "name"       : file_helper.get_filename( file ),
                                                              "import_date": str( datetime.datetime.now() ) } )
            else:
                self.source_uid = None
            
            if handler.detect_records and not no_count:
                rx = re.compile( handler.detect_records )
                num_records = 0
                
                with MCMD.action( "Counting records" ) as action:
                    with open( file, "r" ) as file_in:
                        for line in file_in:
                            if rx.match( line ):
                                num_records += 1
                                action.increment()
            else:
                num_records = -1
            
            title = "Iterating {}".format( file_helper.get_filename( file ) )
            
            with MCMD.action( title, count = num_records, text = lambda _: "{} nodes, {} edges".format( self.endpoint.num_nodes, self.endpoint.num_edges ) ) as action:
                self.action = action
                with open( file, "r" ) as file_in:
                    for record in SeqIO.parse( file_in, handler.code ):
                        self.__process_line( record, biopython_extraction )
                        action.increment()
        
        
        @staticmethod
        def __parse_user_edges_argument( create_edges ):
            create_edges_list = [ ]
            if create_edges:
                for x in create_edges:
                    xx = x.split( "=" )
                    if len( xx ) != 2:
                        raise ValueError( "The `create_edges` parameter expects key=value pairs: «{}» is invalid.".format( x ) )
                    
                    create_edges_list.append( xx )
            
            return create_edges_list
        
        
        def __read_id( self, id: str, props ) -> None:
            """
            FASTA contains other garbage that isn't in the GB, so to stay compatible we remove it
            This only works for GB fasta files and similar (i.e. where the true ID is the last element of the provided ID)
            """
            elements = id.split( "|" )
            
            if self.id_parts:
                if len( elements ) != len( self.id_parts ):
                    raise ValueError( "The ID «{}» is not compatible with the ID format specified: «{}». Maybe you meant to specify a different format?".format( id, "|".join( self.id_parts ) ) )
                
                for index, property in enumerate( self.id_parts ):
                    if property:
                        props[ _make_property_name( property, "" ) ] = elements[ index ]
            
            if not self.id_part_has_uid:
                assert constants.PROP_ALL_PRIMARY_KEY not in props
                props[ constants.PROP_ALL_PRIMARY_KEY ] = id.strip()
            
            assert constants.PROP_ALL_PRIMARY_KEY in props, "Internal error. ID parsed: «{}». No «{}» in properties: {}".format( id, constants.PROP_ALL_PRIMARY_KEY, props )
            assert props[ constants.PROP_ALL_PRIMARY_KEY ], "Internal error. ID parsed: «{}». Invalid «{}» in properties: {}".format( id, constants.PROP_ALL_PRIMARY_KEY, props )
        
        
        def __process_line( self, record: SeqRecord, true_extract: bool ) -> None:
            #
            # Record node
            #
            annotation_references, props, uid = self.__mk_record_node( record )
            
            #
            # Features
            #
            if self.include_features:
                for f in record.features:  # type:SeqFeature
                    self.__mk_feature( f, record, uid, true_extract )
                    self.action.still_alive()
            
            #
            # References
            #
            if self.include_references:
                for key, value in annotation_references.items():
                    self.__mk_reference_node( key, uid, value )
                    self.action.still_alive()
            
            #
            # Source edge
            if self.source_uid is not None:
                self.__mk_source_edge( uid )
            
            # 
            # User edges
            #
            if self.create_edges:
                for property, label in self.create_edges:
                    self.__mk_user_edge( label, property, props, uid )
                    self.action.still_alive()
        
        
        def __mk_record_node( self, record: SeqRecord ):
            """
            Creates a `Node` from a `SeqRecord`.
            """
            #
            # Truncate superfluous information
            #
            
            # - ignore record name if it is the same as the ID
            record_name = record.name
            
            if record_name == record.id:
                record_name = None
            
            # - truncate the part of the description that is the same as the ID
            description = record.description
            if description.startswith( record.id ):
                description = description[ len( record.id ): ].lstrip()
            
            # - simplify the alphabet name
            alphabet_name = _alphabet_shortcode( record.seq.alphabet )
            
            #
            # Create the property dictionary
            #
            props = { }
            props[ "source_id" ] = record.id
            props[ "sequence_alphabet" ] = alphabet_name
            if self.include_record_sequence:
                props[ "sequence" ] = str( record.seq )
            if record_name:
                props[ "name" ] = record_name
            if len( record.letter_annotations ):
                props[ "letter_annotations_count" ] = len( record.letter_annotations )
            if len( record.dbxrefs ):
                props[ "dbxrefs" ] = record.dbxrefs
            if len( record.seq ):
                props[ "sequence_length" ] = len( record.seq )
            if len( record.features ):
                props[ "features_count" ] = len( record.features )
            if len( record.annotations ):
                props[ "annotations_count" ] = len( record.annotations )
            if description:
                props[ "description" ] = description
            self.__read_id( record.id, props )
            annotation_references = { }
            
            #
            # Dictionary annotations get expanded
            #
            annotations = { }
            if self.include_annotations:
                for key, value in record.annotations.items():
                    def recursive_add( target_1, key_1, value_1 ):
                        if type( value_1 ) in [ dict, defaultdict ]:
                            for key_2, value_2 in value_1.items():
                                recursive_add( target_1, key_1 + "_" + key_2, value_2 )
                        else:
                            target_1[ key_1 ] = value_1
                    
                    
                    recursive_add( annotations, key, value )
                
                #
                # Convert annotations to properties with a leading "_"
                #
                for key, value in annotations.items():
                    if not value:
                        # Don't add empty annotations
                        continue
                    if type( value ) in NEO_TYPE_COLLECTION.by_type:
                        # Add all standard typed annotations
                        props[ _make_property_name( key ) ] = value  # if this is the wrong type it will get caught later
                    elif (type( value ) == list) and (array_helper.list_type( value ) in NEO_TYPE_COLLECTION.by_type):
                        # Add lists of standard typed annotations
                        props[ _make_property_name( key ) ] = value
                    elif type( value ) == Reference:
                        # Add references in their own special set
                        annotation_references[ key ] = value
                    elif (type( value ) == list) and (array_helper.list_type( value ) == Reference):
                        # Add lists of references
                        for i, vv in enumerate( value ):
                            if type( vv ) == Reference:
                                annotation_references[ key + "_" + str( i ) ] = vv
                    else:
                        raise NotImplementedError( "InstanceHandler not implemented for annotation type. Regarding annotation «{0}» of value «{1}» and type «{2}» within sequence «{3}»".format( key, value, type( value ).__name__, record.id ) )
            
            #
            # Write
            #
            uid = props[ constants.PROP_ALL_PRIMARY_KEY ]
            del props[ constants.PROP_ALL_PRIMARY_KEY ]
            self.endpoint.endpoint_create_node( label = self.record_label,
                                                uid = uid,
                                                properties = props )
            
            return annotation_references, props, uid
        
        
        def __mk_user_edge( self, label: str, property: str, record_props: Dict[ str, Optional[ object ] ], uid: str ):
            value = record_props.get( property )
            
            if value:
                if label == "Taxon" and self.taxonomy_names_list is not None:
                    taxon_uid = self.taxonomy_names_list.get( value )
                    
                    if taxon_uid is None:
                        raise ValueError( "Cannot get the UID of the taxon named «{}» in the sequence with UID = «{}».".format( value, uid ) )
                    
                    value = taxon_uid
                
                self.endpoint.endpoint_create_edge( label = "Contains",
                                                    start_label = label,
                                                    start_uid = value,
                                                    end_label = self.record_label,
                                                    end_uid = uid,
                                                    properties = { } )
        
        
        def __mk_source_edge( self, record_uid: str ):
            self.endpoint.endpoint_create_edge( label = constants.EDGE_FILE_CONTAINS_SEQUENCE,
                                                start_label = constants.NODE_SOURCE,
                                                start_uid = self.source_uid,
                                                end_label = self.record_label,
                                                end_uid = record_uid,
                                                properties = { } )
        
        
        def __mk_reference_node( self, reason: str, record_uid: str, reference: Reference ):
            reference_name = _get_unique_id( reference )
            location = LocationExtract( reference.location )
            self.endpoint.endpoint_create_node( label = constants.NODE_REFERENCE,
                                                uid = reference_name,
                                                properties = {
                                                    "authors"            : reference.authors,
                                                    "comment"            : reference.comment,
                                                    "consrtm"            : reference.consrtm,  # I presume this is "consortium", but I haven't translated it because I cannot find any documentation to that effect
                                                    "journal"            : reference.journal,
                                                    "location_start"     : location.start,
                                                    "location_end"       : location.end,
                                                    "location_start_type": location.start_type,
                                                    "location_end_type"  : location.end_type,
                                                    "title"              : reference.title,
                                                    "medline_id"         : reference.medline_id,
                                                    "pubmed_id"          : reference.pubmed_id
                                                } )
            
            self.endpoint.endpoint_create_edge( label = constants.EDGE_SEQUENCE_REFERENCES_REFERENCE,
                                                start_label = self.record_label,
                                                start_uid = record_uid,
                                                end_label = constants.NODE_REFERENCE,
                                                end_uid = reference_name,
                                                properties = { "reason": reason } )
        
        
        class MSubset:
            def __init__( self, record: SeqRecord, location: LocationExtract ):
                self.record = record
                self.location = location
            
            
            @property
            def seq( self ) -> str:
                return self.record.seq[ self.location.start:self.location.end ]  # TODO: Check this, should it be inclusive?
            
            
            @property
            def features( self ) -> Iterator[ SeqFeature ]:
                for feature in self.record.features:
                    location = LocationExtract( feature.location )
                    
                    if self.location.start <= location.end and location.start <= self.location.end:
                        yield feature
        
        
        def __mk_feature( self, feature: SeqFeature, record: SeqRecord, record_uid: str, true_extract: bool ):
            """
            Converts a `SeqFeature` to a `Node`.
            """
            location = LocationExtract( feature.location )
            
            if true_extract:
                record_subset = feature.extract( record )  # type: SeqRecord
            else:
                record_subset = self.MSubset( record, location )
            
            props = { }
            
            for key, value in feature.qualifiers.items():
                if key == "db_xref":
                    for db_xref in value:
                        db, _ = db_xref.split( ":", 1 )
                        props[ "db_xref" + _make_property_name( db ) ] = db_xref
                else:
                    if self.include_qualifiers:
                        props[ _make_property_name( key ) ] = array_helper.decomplex( value )
            
            props[ "type" ] = feature.type
            props[ "location_start" ] = location.start
            props[ "location_end" ] = location.end
            props[ "location_start_type" ] = location.start_type
            props[ "location_end_type" ] = location.end_type
            
            # Include sequence data
            if self.include_feature_sequence:
                props[ "sequence" ] = record_subset.seq
            
            # The `translation` is annoying, get rid
            if "_translation" in props:
                del props[ "_translation" ]
            
            feature_label, feature_uid = self.__get_feature_label_and_uid( feature, record_uid, location )
            
            self.endpoint.endpoint_create_node( label = feature_label,
                                                uid = feature_uid,
                                                properties = props )
            
            self.endpoint.endpoint_create_edge( label = constants.EDGE_SEQUENCE_CONTAINS_FEATURE,
                                                start_label = self.record_label,
                                                start_uid = record_uid,
                                                end_label = feature_label,
                                                end_uid = feature_uid,
                                                properties = { } )
            
            for f2 in record_subset.features:
                f2_label, f2_uid = self.__get_feature_label_and_uid( f2, record_uid )
                
                f_key = feature_label + "|" + feature_uid
                f2_key = f2_label + "|" + f2_uid
                
                if f2_key >= f_key:
                    continue  # Only create 1 edge
                
                self.endpoint.endpoint_create_edge( label = constants.EDGE_FEATURE_OVERLAPS_FEATURE,
                                                    start_label = feature_label,
                                                    start_uid = feature_uid,
                                                    end_label = f2_label,
                                                    end_uid = f2_uid,
                                                    properties = { } )
        
        
        def __get_feature_label_and_uid( self, feature: SeqFeature, record_uid: str, location = None ):
            uid = feature.id
            
            if uid:
                uid = "{}_{}".format( record_uid, uid )
            else:
                if location is None:
                    location = LocationExtract( feature.location )
                
                uid = "{}[{}:{}]".format( record_uid, location.start, location.end )
            
            label = self.record_label + "_" + string_helper.capitalise_first( string_helper.make_name( feature.type ) )
            
            return label, uid

parser_sequence = ParserSequence.instance


def _make_property_name( key, prefix = "_" ):
    return prefix + string_helper.make_name( key )


__ALPHABET = None


def __alphabet():
    from Bio import Alphabet
    from Bio.Alphabet import IUPAC
    
    global __ALPHABET
    
    if __ALPHABET:
        return __ALPHABET
    else:
        __ALPHABET = {
            Alphabet.SingleLetterAlphabet: "S",
            Alphabet.ProteinAlphabet     : "P",
            Alphabet.NucleotideAlphabet  : "N",
            Alphabet.DNAAlphabet         : "D",
            Alphabet.RNAAlphabet         : "R",
            Alphabet.SecondaryStructure  : "SS",
            Alphabet.ThreeLetterProtein  : "3P",
            IUPAC.ExtendedIUPACProtein   : "xp",
            IUPAC.IUPACProtein           : "p",
            IUPAC.IUPACAmbiguousDNA      : "ad",
            IUPAC.ExtendedIUPACDNA       : "xd",
            IUPAC.IUPACAmbiguousRNA      : "ar",
            IUPAC.IUPACUnambiguousRNA    : "ur" }
        
        return __ALPHABET


def _alphabet_shortcode( a: Optional[ Alphabet ] ) -> Optional[ str ]:
    """
    Use alphabet short-codes to avoid polluting the database with long strings
    """
    alphabet = __alphabet()
    if type( a ) in alphabet:
        return alphabet[ type( a ) ]
    
    t = str( a )
    TRUNCATE = "Alphabet()"
    if t.endswith( TRUNCATE ):
        return t[ 0:-len( TRUNCATE ) ]
    else:
        return t


def _get_unique_id( x: Reference ) -> str:
    """
    Since there doesn't seem to be any consistency in the journal formats, this creates one
    It won't work for even slightly different formats, but at least comes up with something that will work for the same file
    """
    
    if x.pubmed_id:
        return x.pubmed_id
    
    if x.medline_id:
        return x.medline_id
    
    author = string_helper.first_words( x.authors )
    title = string_helper.first_words( x.title )
    journal = string_helper.first_words( x.journal )
    
    return author + "/" + title + "/" + journal

@help_command()
def id_parts_help():
    """
    Many FASTA files have identifiers in a `|` separated format, e.g.
    
       `>eggs|beans|spam`
       
    * The `beans` sequence
    * The `eggs` database
    * The `spam` organism.
    
    The `id_parts` parameter on `import_sequences` allows you to pull apart these identifiers.
    Specify a list of strings denoting the names of the properties for each component, e.g.
    
       `sequence,database,organism`
    
    You should specify as many values as are in your FASTA file.
    Values may be blank, in which case these parts of the identifier are ignored.
    You can use one of these properties as the `uid` of the node.
    If not at least one of these is `uid`, the entirety of the FASTA text is used as the
    UID (`eggs|beans|spam` in the example above).
    
    A simple example for a common FASTA file with extraneous information is:
    
       `,,,uid,` 
    """
    pass
    
@help_command()
def user_edges_help():
    """
    These are used to create 'X-->CONTAINS-->SEQUENCE' relationships.
                                              
    Specify a list of key-value pairs:
    
       `property=label,property=label`
       
    * `property` is the name of the sequence property used to obtain the UID of the target
    * `label` is the label (node-type) of the target.
       
    Example:
       
       `_organism=Taxon,_plasmid=Plasmid`
    
    A special case is made when 'Taxon' is specified as the `label`. This allows `property` to specify the 
    'scientific_name', rather than the 'uid', providing the `taxa` argument is specified.
    
    Note that for FASTA files, the properties are specified in the `id_parts` argument, but for GENBANK files they
    are automatically inferred from the available data. 
    
    If you have trouble determining what the property names are, you can trial-import a smaller portion of your file, 
    sending the data to the ECHO endpoint.
    """
    pass