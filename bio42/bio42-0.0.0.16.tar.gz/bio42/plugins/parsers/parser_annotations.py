import csv
from typing import Callable, Dict, List, Optional
from intermake import command, MENV, MCMD
from mhelper import Filename, EFileMode, exception_helper, override
from neocommand import IEndpoint

from bio42 import constants
from bio42.plugins.parsers.parser_plugin import ParserFilter, ParserPlugin
from bio42.helpers import bio42b_helper

_EXT_CSV = ".csv"
_EXT_TSV = ".tsv"


@command()
class ParserAnnotations( ParserPlugin ):
    """
    Reads GO/Pfam/IPR annotations from CSV/TSV files, creating edges from each sequence to those annotations on that sequence.
    
    Notice:
    The annotation nodes themselves are not created by this parser, other parsers such as `ParserGo` should be run first in order to take care of that.
    
    The parser reads the following CSV columns:
        `uid` - denotes the Sequence UID (must match the UIDs in the database)
        `X` - denotes the respective annotation class IDs, where X is the label of the annotation class. i.e. "Go" "Pfam" or "Ipr" (although you can use your own).
        `X.name` - denotes the names of the classes. This is optional and you probably don't want it if you're not creating the classes.
        
    * Classes will be generated if `create` is specified.
    * Classes will be not be given a `name` property if no `X.name` column is specified.
    * To save database space, redundant information in IDs for non-custom classes is stripped, e.g. 'GO:0000001` --> '0000001'.
        
    CSV file properties:
        COL-NAMES        = Yes
        ROW-NAMES        = No
        DELIMITER (CSV)  = ,
        DELIMITER (TSV)  = Tab
        QUOTES           = "
        RECORD           = System line break
        MULTILINE-QUOTES = Supported
    """
    
    
    def __init__( self ):
        extensions = [ ParserFilter( "CSV", ".csv", "Comma separated value files" ),
                       ParserFilter( "TSV", [ ".tsv", ".tab" ], "Tab separated value files" ) ]
        
        super().__init__( "Annotations", extensions )
    
    
    @override
    def iterate_file( self, endpoint: IEndpoint, 
                      file_name: Filename[EFileMode.READ, _EXT_CSV, _EXT_TSV], 
                      create_classes: bool = False, 
                      viable_columns: Optional[ List[ str ] ] = None, 
                      name_delimiter: str = "|", 
                      uid_delimiter: str = "|", 
                      permit_custom: bool = False,
                      pad: Optional[ bool ] = None ) -> None:
        """
        OVERRIDE
        :param endpoint:    Where to send the parsed data to. 
        :param file_name:   File to read in.
        :param create_classes: Whether to create the classes.
        :param viable_columns: Which columns to accept. If not specified all columns are assumed. The `uid` column is implicit and need not be specified.
        :param name_delimiter: Delimiter for multiple class UIDs in the same column.
        :param uid_delimiter: Delimiter for multiple class names in the same column.
        :param permit_custom: Permit use of custom classes (i.e. not `Go`, `Pfam`, `Ipr` or `Kegg`).
        :param pad: Treat missing columns as empty. This is the default for TSV but not for CSV.
        """
        if file_name.endswith( ".csv" ):
            delimiter = ","
            if pad is None:
                pad = False
        elif file_name.endswith( ".tsv" ):
            delimiter = "\t"
            if pad is None:
                pad = True
        else:
            raise ValueError( "File must end with <.csv> or <.tsv> but «{0}» does not.".format( file_name ) )
        
        uids_used = { }
        
        with open( file_name, "r" ) as file_in:
            reader = csv.reader( file_in, delimiter = delimiter )
            
            col_names = next( reader )
            
            col_id = None
            col_class = { }
            col_fixer = { }
            col_class_name = { }
            
            NAME_KEY_SUFFIX = ".name"
            
            for i, col_name in enumerate( col_names ):
                if col_name == "uid":
                    col_id = i
                else:
                    if viable_columns is not None and col_name not in viable_columns:
                        continue
                    
                    if col_name.endswith( NAME_KEY_SUFFIX ):
                        col_class_name[ col_name[ :len( NAME_KEY_SUFFIX ) ] ] = i
                    else:
                        col_class[ col_name ] = i
                        
                        if col_name == constants.NODE_GOCLASS:
                            fixer = bio42b_helper.go_id_to_uid
                        elif col_name == constants.NODE_PFAMCLASS:
                            fixer = bio42b_helper.pfam_id_to_uid
                        elif col_name == constants.NODE_IPRCLASS:
                            fixer = bio42b_helper.ipr_id_to_uid
                        elif col_name == constants.NODE_KEGGCLASS:
                            fixer = bio42b_helper.kegg_id_to_uid
                        elif permit_custom:
                            fixer = str
                        else:
                            raise ValueError( "Cannot read the file «{0}» because the «{1}» class-column is not recognised by " + MENV.name + " and the <custom> argument is not set. Specify the <custom> argument or use the <columns> argument to specify only those columns you wish to use. The columns present are «{2}».".format( file_name, col_name, col_names ) )
                        
                        col_fixer[ col_name ] = fixer
            
            for key in col_class_name:
                if key not in col_class:
                    raise ValueError( "Cannot read the file «{0}» because whilst there is a <.name> column for «{1}» (<{1}.name>), there is no UID column («{1}»). The columns present are «{2}».".format( file_name, key, col_names ) )
            
            if col_id is None:
                raise ValueError( "Cannot read the file «{0}» because none of the mandatory <uid> column does not exist. The columns present are «{1}».".format( file_name, col_names ) )
            
            if not col_class:
                raise ValueError( "Cannot read the file «{0}» because it doesn't contain any other accepted columns. The columns present are «{1}».".format( file_name, col_names ) )
            
            for key, value in col_class.items():
                name = col_class_name.get( key )
                uids_used[ key ] = { }
                fixer = col_fixer[ key ]
                
                if name is not None:
                    MCMD.print( "«{}» in column «{}» with name in column «{}». Mapped using «{}».".format( key, value, name, fixer.__name__ ) )
                else:
                    MCMD.print( "«{}» in column «{}». Mapped using «{}».".format( key, value, fixer.__name__ ) )
            
            with MCMD.action( "Creating edges" ) as action:
                for i, row in enumerate( reader ):
                    action.increment()
                    sequence = row[ col_id ]
                    
                    for annotation_class, col_index in col_class.items():
                        annotation_class_name = col_class_name.get( annotation_class )
                        fixer = col_fixer.get( annotation_class )
                        self.__apply_annotation( row_index = i,
                                                 endpoint = endpoint,
                                                 sequence = sequence,
                                                 row = row,
                                                 uids_used = uids_used[ annotation_class ],
                                                 col_uid = col_index,
                                                 col_name = annotation_class_name,
                                                 label = annotation_class,
                                                 edge_label = constants.EDGE_GOCLASS_CONTAINS_SEQUENCE,
                                                 fixer = fixer,
                                                 name_delimiter = name_delimiter,
                                                 uid_delimiter = uid_delimiter,
                                                 pad = pad )
            
            if create_classes:
                for class_, name_dict in uids_used.items():
                    with MCMD.action( "Creating «{}» nodes".format( class_ ), len( name_dict ) ) as action:
                        for uid, name in name_dict.items():
                            if name:
                                data = { "name": name }
                            else:
                                data = { }
                            
                            action.increment()
                            endpoint.endpoint_create_node( label = class_, uid = uid, properties = data )
    
    
    @staticmethod
    def __apply_annotation( row_index: int,
                            endpoint: IEndpoint,
                            sequence: str,
                            row: List[ str ],
                            uids_used: Dict[ str, Optional[ str ] ],
                            col_uid: int,
                            col_name: Optional[ int ],
                            label: str,
                            edge_label: str,
                            fixer: Callable[ [ str ], str ],
                            name_delimiter,
                            uid_delimiter,
                            pad ) -> None:
        if col_uid < 0 or col_uid >= len( row ):
            if pad:
                return
            raise KeyError( "Row does not have column «{}», which is specified as the UID, and the <pad> argument is <False>: «{}».".format( col_uid, row ) )
        
        uid_text = row[ col_uid ]
        
        if col_name is None:
            name_texts = None
        else:
            name_text = row[ col_name ]
            name_texts = name_text.split( name_delimiter )
        
        for i, row_text in enumerate( uid_text.split( uid_delimiter ) ):
            if row_text:
                try:
                    uid = fixer( row_text )
                except Exception as ex:
                    exception_helper.add_details( ex, row_index = row_index, uid_column_index = col_uid, name_column_index = col_name )
                    raise
                
                if name_texts is not None:
                    name = name_texts[ i ]
                else:
                    name = None
                
                uids_used[ uid ] = name
                
                endpoint.endpoint_create_edge( label = edge_label, start_label = label, start_uid = uid, end_label = constants.NODE_SEQUENCE, end_uid = sequence, properties = { } )



