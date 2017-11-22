"""
This test assumes Neo4j is installed, running, and contains an empty database
Paths may require fixing before commencing the test
"""
from os import path

import bio42
import neocommand
import intermake
from mhelper import Password


ENDPOINT_DB_NAME = "testdb"
ENDPOINT_CSV_NAME = "testcsv"
SAMPLE_FOLDER = path.join( path.split( __file__ )[0], "sample_data" )
GENBANK = path.join( SAMPLE_FOLDER, "sample.gb" )
TAX_HIERARCHY = path.join( SAMPLE_FOLDER, "sample.taxh" )
TAX_NAMES = path.join( SAMPLE_FOLDER, "sample.taxn" )
BLAST = path.join( SAMPLE_FOLDER, "sample.blast" )

# Create our database endpoint
neocommand.endpoints.new_connection( name = ENDPOINT_DB_NAME,
                                     driver = neocommand.ENeo4jDriver.NEO4JV1,
                                     host = "127.0.0.1",
                                     user = "neo4j",
                                     password = Password( "localpass" ),
                                     directory = path.expanduser( "~/bin/neo4j330" ),
                                     unix = True,
                                     windows = False,
                                     port = "7474" )

# Create our parcel
neocommand.endpoints.new_parcel( name = ENDPOINT_CSV_NAME )

# Import the taxonomy data
bio42.parser_taxonomy.parser_taxonomy( endpoint = ENDPOINT_CSV_NAME,
                                       file_name = TAX_HIERARCHY,
                                       names_file_name = TAX_NAMES )

# Import our GenBank data
bio42.parser_sequence.parser_sequence( file = GENBANK,
                                       endpoint = ENDPOINT_CSV_NAME,
                                       include_source = True,
                                       include_record_sequence = True,
                                       include_feature_sequence = True,
                                       include_references = True,
                                       include_features = True,
                                       include_qualifiers = True,
                                       include_annotations = True,
                                       id_parts = None,
                                       user_edges = "_organism=Taxon",
                                       taxonomy_file = TAX_NAMES,
                                       record_label = "Record",
                                       biopython_extraction = False,
                                       no_count = False )

# Import our BLAST data
bio42.parser_blast.parser_blast( file_name = BLAST,
                                 endpoint = ENDPOINT_CSV_NAME,
                                 column_names = None,
                                 dictionary_file_name = None,
                                 dictionary_uid_column = -1,
                                 deep_query = True )
