u"""
Methods for dealing with Neo4j CSV files.

See the Neo4j documentation for details on the format.
"""

import csv
from os import path
from typing import Dict, List, Optional, Union

from mhelper import MEnum
from intermake import EColour, IVisualisable, UiInfo
from mhelper import SwitchError, array_helper, file_helper
from neocommand.data import constants
from neocommand.database.entities import Edge, Node
from neocommand.gui_qt import resources as Res
from progressivecsv import ProgressiveCsvHeader, ProgressiveCsvWriter


__author__ = "Martin Rusilowicz"


class NeoType:
    """
    Represents a neo4j type.
    
    :data neo4j_name:   Name in Neo4j
    :data element_type: Python type (never an array)
    :data is_array:     Is this an array
    :data ARRAY:        Array equivalent
    :data NO_ARRAY:     Not-an-array equivalent
    """
    
    
    def __init__( self, neo4j_name, element_type, parent = None ):
        self.neo4j_name = neo4j_name
        self.element_type = element_type
        
        if parent is None:
            self.is_array = False
            self.ARRAY = NeoType( neo4j_name + "[]", element_type, self )
            self.NO_ARRAY = self
        else:
            self.is_array = True
            self.ARRAY = self
            self.NO_ARRAY = parent
        
        assert self.ARRAY is not None
        assert self.NO_ARRAY is not None
    
    
    def string_to_value( self, text: str ) -> object:
        """
        Given a `text` string, convert it into a (Python) value of this type.
        """
        if self.is_array:
            return [self.NO_ARRAY.string_to_value( x ) for x in text.split( ";" )]
        else:
            return self.element_type( text )
    
    
    def __str__( self ):
        return "Neo4j::{} ({}{})".format( self.neo4j_name, "LIST OF " if self.is_array else "", self.element_type )
    
    
    def to( self, neo_type: "NeoType" ):
        if self.is_array:
            return neo_type.ARRAY
        else:
            return neo_type.NO_ARRAY


class NeoTypeCollection:
    """
    Collection of available `NeoType`s.
    """
    
    
    def __init__( self ):
        self.INT = NeoType( "int", int )
        self.FLOAT = NeoType( "float", float )
        self.STR = NeoType( "string", str )
        self.BOOL = NeoType( "boolean", bool )
        self.__all = [self.INT, self.FLOAT, self.STR, self.BOOL]
        self.__all_arrays = list( self.__all )
        self.__all_arrays.extend( x.ARRAY for x in self.__all )
        self.by_name = dict( (x.neo4j_name, x) for x in self.__all_arrays )
        self.by_type = dict( (x.element_type, x) for x in self.__all )
    
    
    def from_name( self, text: str ) -> NeoType:
        """
        Find the type from the name.
        """
        return self.by_name[text]
    
    
    def from_type( self, element_type: type ):
        """
        Find the type from the `element_type` (never an array).
        """
        return self.by_type[element_type]


NEO_TYPE_COLLECTION = NeoTypeCollection()
NEO_FALSE = "false"
NEO_TRUE = "true"  # Note the only root_object neo4j sees as True for a boolean property is "true", everything else (even "1" and "True") is False, apart from "", which is null.


class NeoCsvFilename( IVisualisable ):
    """
    We use specific filenames for the Neo4j CSVs, this class creates and interprets them.
    
        node-label.extension
        edge-source-label-destination.extension
        
    Use methods:
    
        construct_from_node
        construct_from_edge
        construct_from_file
    """
    
    
    def __init__( self, file_name: str, is_edge: bool, label: str, start_label: Optional[str], end_label: Optional[str] ):
        self.filename = file_name
        self.alone = file_helper.get_filename_without_extension( file_name )
        self.is_edge = is_edge
        self.label = label
        self.start_label = start_label
        self.end_label = end_label
    
    
    def remove_from_disk( self ):
        if path.isfile( self.filename ):
            file_helper.recycle_file( self.filename )
        else:
            raise ValueError( "Cannot delete this file because it doesn't exist «{0}»".format( self.filename ) )
    
    
    def __str__( self ):
        return self.label
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = file_helper.get_filename_without_extension( self.filename ),
                       comment = self.filename,
                       type_name = "Csv/Neo4j",
                       value = "{}({}>{})".format( self.label, self.start_label, self.end_label ) if self.is_edge else self.label,
                       colour = EColour.BLUE,
                       icon = Res.edge if self.is_edge else Res.node,
                       extra = { "filename"   : self.filename,
                                 "alone"      : self.alone,
                                 "is_edge"    : self.is_edge,
                                 "start_label": self.start_label,
                                 "end_label"  : self.end_label } )
    
    
    @classmethod
    def construct_from_node( cls, folder_path: str, label: str ):
        assert label, "Invalid node label (blank)"
        file_name = path.join( folder_path, constants.FILENAME_NODE_PREFIX + "-" + label ) + constants.EXT_B42CSV
        return cls( file_name, False, label, None, None )
    
    
    @classmethod
    def construct_from_edge( cls, folder_path, label: str, start_label: str, end_label: str ):
        assert label, "Invalid edge label (blank)"
        assert start_label, "Invalid start_label (blank)"
        assert end_label, "Invalid end_label (blank)"
        file_name = path.join( folder_path, constants.FILENAME_EDGE_PREFIX + "-" + start_label + "-" + label + "-" + end_label ) + constants.EXT_B42CSV
        return cls( file_name, True, label, start_label, end_label )
    
    
    @classmethod
    def construct_from_file( cls, file_name ):
        filename_parts = file_helper.get_filename_without_extension( file_name ).split( "-" )
        
        if filename_parts[0] == constants.FILENAME_NODE_PREFIX:
            # Nodes
            assert len( filename_parts ) == 2, "I don't understand the node-table filename «{}» because I expected it to have 2 parts but I got {}.".format( file_name, filename_parts )
            return cls( file_name, False, filename_parts[1], None, None )
        elif filename_parts[0] == constants.FILENAME_EDGE_PREFIX:
            # Edges
            assert len( filename_parts ) == 4, "I don't understand the edge-table filename «{}» because I expected it to have 4 parts but I got {}.".format( file_name, filename_parts )
            return cls( file_name, True, filename_parts[2], filename_parts[1], filename_parts[3] )
        else:
            # Something else :(
            raise ImportError( "A 'NeoCsvFilename' cannot be constructed from the filename «{0}» because it is not a valid " + constants.APP_DISPLAY_NAME + " filename.".format( file_name ) )


class ENeoCsvSpecialHeader( MEnum ):
    NONE = 0
    UID = 1
    START = 2
    END = 3


class NeoCsvHeader:
    """
    Represents a header (column) of a NeoCsv file.
    
    Access:
        .name               - to get the name (fixed). This is how we see it.
        .decorated_name()   - to get the name, type and label (if required). This is what is actually written to the file.
        
    Use:
        .parse(...)         - to interpret existing
        .from_value(...)    - to create new
    
    The supported column types are:
        * int, long, float, double, boolean, byte, short, char, string
        * And lists thereof
    """
    
    
    def __init__( self, name: Optional[str], type_: Optional[NeoType], special: ENeoCsvSpecialHeader ):
        """
        CONSTRUCTOR
        :param name: Name of the header
        :param type_: Type of the header (must be a neotype, or NoneType, which will be converted to the most restrictive type "bool")
        """
        if special == ENeoCsvSpecialHeader.NONE:
            if name is None:
                raise ValueError( "The `name` of a NeoCsvHeader cannot be `None` when the header is not marked as having a special case handler." )
            
            if type_ is None:
                raise ValueError( "The `type_` of a NeoCsvHeader cannot be `None` when the header is not marked as having a special case handler." )
        
        if name:
            if ":" in name:
                raise ValueError( "Invalid name for a NeoCsvHeader: «{}».".format( name ) )
        
        self.__name = name  # type:str
        self.__type = type_  # type:NeoType
        self.__special = special
    
    
    @property
    def name( self ) -> str:
        """
        Obtains the name of this column (with no type decoration)
        """
        return self.__name
    
    
    @property
    def type( self ) -> NeoType:
        """
        Obtains the `NeoType` of this column.
        """
        return self.__type
    
    
    @property
    def special( self ) -> ENeoCsvSpecialHeader:
        """
        Obtains any special status of this column.
        """
        return self.__special
    
    
    def __str__( self ):
        """
        String representation of this column, for debugging.
        """
        if self.__special == ENeoCsvSpecialHeader.NONE:
            return "NeoCsvHeader({} : {}{})".format( self.__name, self.__type, "[]" if self._is_array else "" )
        else:
            return "NeoCsvHeader(special = {})".format( self.__special )
    
    
    def decorated_name( self, file: "NeoCsvFilename" ) -> str:
        """
        Gets the fully decorated column name, including name and type
        """
        if self.__special == ENeoCsvSpecialHeader.UID:
            if file.is_edge:
                raise ValueError( "Column is a UID but the file given is an EDGE." )
            
            return constants.PRIMARY_KEY_DECORATED_NAME + "(" + file.label + ")"
        elif self.__special == ENeoCsvSpecialHeader.START:
            if not file.is_edge:
                raise ValueError( "Column is a START_ID but the file given is not an EDGE." )
            
            return constants.NEO4J_START_ID_SUFFIX + "(" + file.start_label + ")"
        elif self.__special == ENeoCsvSpecialHeader.END:
            if not file.is_edge:
                raise ValueError( "Column is an END_ID but the file given is not an EDGE." )
            
            return constants.NEO4J_END_ID_SUFFIX + "(" + file.end_label + ")"
        elif self.__special == ENeoCsvSpecialHeader.NONE:
            return self.__name + ":" + self.__type.neo4j_name
        else:
            raise SwitchError( "special", self.__special )
    
    
    def encompass_value( self, value: object ) -> bool:
        """
        Given an existing type and a value, returns the type that would encompass them both the existing data and the new data, if read from a CSV
        """
        if self.__special != ENeoCsvSpecialHeader.NONE:
            if not isinstance( value, str ):
                raise ValueError( "A column of special type «{}» only expected a 'str' value, but the value provided is {} {}.".format( self.__special, type( value ), value ) )
            
            return False
        
        # All floats are strings
        # All ints are floats
        # All bools are ints
        # Nothing can be anything
        
        changes = False
        
        if type( value ) == list:
            the_list = value  # type:List
            
            if len( the_list ) == 0:
                return changes
            elif len( the_list ) == 1:
                type_ = type( the_list[0] )
            else:
                type_ = array_helper.list_type( value )
                if not self.__type.is_array:
                    self.__type = self.__type.ARRAY
                    changes = True
        else:
            type_ = type( value )
        
        if type_ is type( None ):
            # Doesn't matter then!
            return changes
        
        if self.__type.NO_ARRAY is NEO_TYPE_COLLECTION.STR:
            if (value is None) or (type_ in [str, float, int, bool]):
                return changes
        elif self.__type.NO_ARRAY is NEO_TYPE_COLLECTION.FLOAT:
            if (value is None) or (type_ in [float, int, bool]):
                return changes
            elif type_ is str:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.STR )
                return True
        elif self.__type.NO_ARRAY is NEO_TYPE_COLLECTION.INT:
            if (value is None) or (type_ in [int, bool]):
                return changes
            elif type_ is float:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.FLOAT )
                return True
            elif type_ is str:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.STR )
                return True
        elif self.__type.NO_ARRAY is NEO_TYPE_COLLECTION.BOOL:
            if (value is None) or (type_ in [bool]):
                return changes
            if type_ is int:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.INT )
                return True
            elif type_ is float:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.FLOAT )
                return True
            elif type_ is str:
                self.__type = self.__type.to( NEO_TYPE_COLLECTION.STR )  # type: NeoType
                return True
        
        raise ValueError( "Cannot work out how to encompass a new value «{}» of type «{}» into the data column «{}» which is of type «{}».".format( value, type_, self.__name, self.__type ) )
    
    
    @staticmethod
    def from_decorated_name( file: NeoCsvFilename, decorated_name: str ) -> "NeoCsvHeader":
        """ 
        Translates a header's decorated name into a NeoCsvHeader object.
        
        :param file: The file we are reading from.
        :param decorated_name: A decorated name of one of the forms:
        
                                    1. name:type
                                    2. uid:ID
                                    3. uid:ID(node_label)
                                    4. :END_ID
                                    5. :END_ID(end_label)
                                    6. :START_ID 
                                    7. :START_ID(start_label)
                                    
                                Note that forms 2, 4 and 6 are supported so the caller can remain ignorant of the label;
                                when written via `decorated_name`, the label will always be included.
                                
        :except ValueError: Invalid name.
        """
        
        if decorated_name.count( ":" ) != 1:
            raise ValueError( "The column name «{}» in the file «{}» isn't a valid NEO4J-style header. The format should be «name:type», but it isn't.".format( decorated_name, file.filename ) )
        
        name, type_name = decorated_name.split( ":", 1 )
        
        if "(" in type_name:
            type_name, label = type_name.split( "(", 1 )  # type: str, str
            
            if ")" not in label:
                raise ValueError( "Invalid decorated name «{}»: Missing parenthesis.".format( decorated_name ) )
            
            label = label.replace( ")", "", 1 ).strip()
        else:
            label = None
        
        if name == constants.PROP_ALL_PRIMARY_KEY or type_name == constants.NEO4J_ID_TYPE:
            # uid:*
            if name != constants.PROP_ALL_PRIMARY_KEY:
                raise ValueError( "Invalid decorated name «{}»: Name of UID should be «{}», not «{}».".format( decorated_name, constants.PROP_ALL_PRIMARY_KEY, name ) )
            
            if type_name != constants.NEO4J_ID_TYPE:
                raise ValueError( "Invalid decorated name «{}»: Type of UID should be «{}», not «{}».".format( decorated_name, constants.NEO4J_ID_TYPE, type_name ) )
            
            if label and label != file.label:
                raise ValueError( "Invalid decorated name «{}»: Label should be the primary key in the file «{}», not «{}».".format( decorated_name, file, label ) )
            
            return NeoCsvHeader( None, None, ENeoCsvSpecialHeader.UID )
        elif type_name == constants.NEO4J_START_ID_TYPE:
            # *:START_ID[(*)]
            if name:
                raise ValueError( "Invalid decorated name «{}»: Name of START_ID should be empty.".format( decorated_name ) )
            
            if label and label != file.start_label:
                raise ValueError( "Invalid decorated name «{}»: Label should be the start label in the file «{}», not «{}».".format( decorated_name, file, label ) )
            
            return NeoCsvHeader( None, None, ENeoCsvSpecialHeader.START )
        elif type_name == constants.NEO4J_END_ID_SUFFIX[1:]:
            # *:END_ID[(*)]
            if name:
                raise ValueError( "Invalid decorated name «{}»: Name of END_ID should be empty.".format( decorated_name ) )
            
            if label and label != file.end_label:
                raise ValueError( "Invalid decorated name «{}»: Label should be the end label in the file «{}», not «{}».".format( decorated_name, file, label ) )
            
            return NeoCsvHeader( None, None, ENeoCsvSpecialHeader.END )
        else:
            if not name:
                raise ValueError( "Invalid decorated name «{}»: Name of should not be blank.".format( decorated_name ) )
            
            if label:
                raise ValueError( "Invalid decorated name «{}»: Label «{}» not expected.".format( decorated_name, label ) )
            
            neo_type = NEO_TYPE_COLLECTION.from_name( type_name )
            return NeoCsvHeader( name, neo_type, ENeoCsvSpecialHeader.NONE )
    
    
    @staticmethod
    def from_value( name: Union[str, ENeoCsvSpecialHeader], value: object ) -> "NeoCsvHeader":
        """
        Given a `name` and `value`, create a suitable `NeoCsvHeader`. 
        :param name:    Name of the header OR a special key
        :param value:   A value to be stored in the column
        :return: A `NeoCsvHeader` object.
        """
        if isinstance( name, ENeoCsvSpecialHeader ):
            if not isinstance( value, str ):
                raise ValueError( "A column of special type «{}» only expected a 'str' value, but the value provided is {} {}.".format( name, type( value ), value ) )
            
            return NeoCsvHeader( None, None, name )
        elif isinstance( name, str ):
            if type( value ) is list:
                the_list = value  # type:List[object]
                if len( the_list ) == 0:
                    return NeoCsvHeader( name, NEO_TYPE_COLLECTION.BOOL.ARRAY, ENeoCsvSpecialHeader.NONE )
                elif len( the_list ) == 1:
                    return NeoCsvHeader( name, NEO_TYPE_COLLECTION.from_type( type( the_list[0] ) ).ARRAY, ENeoCsvSpecialHeader.NONE )
                else:
                    return NeoCsvHeader( name, NEO_TYPE_COLLECTION.from_type( array_helper.list_type( value ) ).ARRAY, ENeoCsvSpecialHeader.NONE )
            else:
                return NeoCsvHeader( name, NEO_TYPE_COLLECTION.from_type( type( value ) ), ENeoCsvSpecialHeader.NONE )
        else:
            raise SwitchError( "name", name, instance = True )


class NeoCsvReader:
    """
    Reads a NeoCsv file.
    
    In contrast to `dictreader`, this parses the headers, stripping extraneous type and label information from the keys in the `dict` returned.
    """
    
    
    def __init__( self, neo_csv_filename: NeoCsvFilename ):
        """
        CONSTRUCTOR
        :param neo_csv_filename: Parsed filename 
        """
        self.file_name = neo_csv_filename.filename
        self._stream = open( self.file_name, "r" )
        self._reader = csv.reader( self._stream, lineterminator = "\n" )
        self._headers = self.__read_all_headers( neo_csv_filename, next( self._reader ) )
    
    
    @staticmethod
    def __read_all_headers( file: NeoCsvFilename, decorated_names: Optional[list] ) -> List[NeoCsvHeader]:
        """
        Static method that reads converts a list of decorated names to a list of headers.
        """
        result = []
        
        if decorated_names:
            for header_text in decorated_names:
                header = NeoCsvHeader.from_decorated_name( file, header_text )
                result.append( header )
        
        return result
    
    
    def next( self ):
        row = self._reader.next()
        
        result = { }
        
        for col_index, cell in enumerate( row ):
            header = self._headers[col_index]
            result[header.name] = header.type.string_to_value( cell )
        
        return result
    
    
    def __iter__( self ):
        while True:
            yield self.next()


class NeoCsvWriter:
    """
    Writes a NeoCsv file.
    
    In contrast to `dictwriter`, this parses the keys, adding extra type and label information to the headers actually written to the file.
    
    In addition, it can append new columns to to existing files, though it does so by rewriting the entirety of the file (which is slow).
    """
    
    
    def __init__( self, neo_csv_filename: NeoCsvFilename ):
        """
        CONSTRUCTOR
        :param neo_csv_filename: Parsed filename 
        """
        self.__file_name = neo_csv_filename
        self.__writer = ProgressiveCsvWriter( neo_csv_filename.filename, on_read = self.__on_read )
    
    
    def write_row( self, row_dict: Dict[Union[str, ENeoCsvSpecialHeader], object] ) -> None:
        """
        Writs a row.
        """
        self.__encompass( row_dict )
        
        # Modify the properties so they are acceptable to a typed csv
        for k, v in list( row_dict.items() ):
            row_dict[k] = self.__translate_to_neo4j( v )
        
        self.__writer.write_row( row_dict )
    
    
    def close( self ):
        """
        Closes the stream (mandatory).
        """
        self.__writer.close()
    
    
    def __on_read( self, header: ProgressiveCsvHeader ) -> None:
        """
        Header creation handler.
        Populates the `tag_neo` property with a `NeoCsvHeader`.
        """
        tag_neo = NeoCsvHeader.from_decorated_name( self.__file_name, header.text )
        header.tag_neo = tag_neo
        header.key = tag_neo.name if tag_neo.special == ENeoCsvSpecialHeader.NONE else tag_neo.special
    
    
    def __encompass( self, row_dict: Dict[str, object] ) -> None:
        """
        Recognise the fields provided by this entity.
        Returns a boolean indicating if any changes have occurred.
        """
        for key, value in row_dict.items():
            header = self.__writer.headers.get( key )
            
            if header is None:
                header = self.__writer.append_header( NeoCsvHeader.from_value( key, value ).decorated_name( self.__file_name ) )
            
            # noinspection PyUnresolvedReferences
            tag_neo = header.tag_neo  # type: NeoCsvHeader
            
            if tag_neo.encompass_value( value ):
                header.text = tag_neo.decorated_name( self.__file_name )
    
    
    def __translate_to_neo4j( self, value ) -> str:
        """
        Given a value, which could be anything, translate it into a string that Neo4j will recognise.
        :param value: Value to convert
        :return: The converted string
        """
        type_ = type( value )
        
        if type_ is list or type_ is tuple:
            # Output a list
            return "\t".join( self.__translate_to_neo4j( x ) for x in value )
        elif type_ is bool:
            return NEO_TRUE if value else NEO_FALSE
        elif type_ in (float, int):
            return str( value )
        elif type_ is str:
            # Quotes cause problems to Neo4j, so get rid of them
            return value.replace( '"', "'" )
        else:
            raise ValueError( "Don't know how to translate the Python type «{}» (value = «{}») into a Neo4j-recognisable string.".format( type_, value ) )


class NeoCsvMultiWriter:
    """
    Used for writing to a NeoCsv folder.
    """
    
    
    def __init__( self, folder_path ):
        self.__folder_path = folder_path
        self.__node_files = { }  # type:Dict[str,  NeoCsvWriter]
        self.__edge_files = { }  # type:Dict[str,  NeoCsvWriter]
    
    
    def write_node( self, node: Node ) -> None:
        """
        Writes the node to the appropriate file. 
        """
        file = self.__node_files.get( node.label )
        
        if file is None:
            file_name = NeoCsvFilename.construct_from_node( self.__folder_path, node.label )
            file = NeoCsvWriter( file_name )
            self.__node_files[node.label] = file
        
        new_props = dict( node.properties )
        new_props[ENeoCsvSpecialHeader.UID] = node.uid
        file.write_row( new_props )
    
    
    def write_edge( self, edge: Edge ) -> None:
        """
        Writes the edge to the appropriate file. 
        """
        key = self.__edge_key( edge.start.label, edge.label, edge.end.label )
        
        file = self.__edge_files.get( key )
        
        if file is None:
            file_name = NeoCsvFilename.construct_from_edge( self.__folder_path, edge.label, edge.start.label, edge.end.label )
            file = NeoCsvWriter( file_name )
            self.__edge_files[key] = file
        
        assert edge.start.uid
        assert edge.end.uid
        
        new_props = dict( edge.properties )
        new_props[ENeoCsvSpecialHeader.START] = edge.start.uid
        new_props[ENeoCsvSpecialHeader.END] = edge.end.uid
        file.write_row( new_props )
    
    
    def any_open( self ) -> bool:
        """
        Returns if any file is open
        :return: 
        """
        return len( self.__node_files ) != 0 or len( self.__edge_files ) != 0
    
    
    def close_all( self ) -> None:
        """
        Finalises and closes all files
        """
        for v in self.__node_files.values():
            v.close()
        
        for v in self.__edge_files.values():
            v.close()
        
        self.__node_files.clear()
        self.__edge_files.clear()
    
    
    @staticmethod
    def __edge_key( start_label, label, end_label ):
        """
        Determines the key of an edge for the internal dictionary.
        """
        return start_label + "," + label + "," + end_label
