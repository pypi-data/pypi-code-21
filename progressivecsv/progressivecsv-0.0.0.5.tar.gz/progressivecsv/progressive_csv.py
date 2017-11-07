"""
Houses the `ProgressiveCsvWriter` class.
"""

import csv

from os import path
import os
from typing import Dict, List, Callable, Optional

from dictionaries import ReadonlyDictProxy, OrderedDict


def _create_index_lookup( the_list: List[ str ] ) -> Dict[ str, int ]:
    """
    Creates a lookup table (`dict`) that allows the index of elements in `the_list` to be found.
    """
    result = { }
    result.update( (v, i) for i, v in enumerate( the_list ) )
    
    return result


class ProgressiveCsvHeader:
    """
    Represents a header of a `ProgressiveCsvWriter`.
    
    Note that the header has both a `key` and `text` property.
    Whilst initially the same, these may be modified by the programmer to provide headers with different keys and texts.
    
    This object is tolerant of external fields (the same reference is always used inside `ProgressiveCsvWriter`).
    """
    
    
    def __init__( self, owner: "ProgressiveCsvWriter", key: str, index: int, header_collection: "Dict[str, ProgressiveCsvHeader]" ):
        """
        CONSTRUCTOR
        :param owner:   Owning `ProgressiveCsvWriter` 
        :param key:     Header key, and default text. 
        :param index:   Header index. 
        """
        self.__owner = owner
        self.__header_collection = header_collection
        self.__key = key
        self.__text = key
        self.__index = index
        self.__header_collection[ self.__key ] = self
    
    
    @property
    def owner( self ) -> "ProgressiveCsvWriter":
        """
        Read-only property that obtains the owning `ProgressiveCsvWriter`.
        """
        return self.__owner
    
    
    @property
    def key( self ) -> str:
        """
        Read-write property that represents the key used when the `ProgressiveCsvWriter.write_row` function is called.
        Since this is an internal key, this may be changed without necessitating that the file is rewritten.
        By default, this is the same as the `text` property.
        """
        return self.__key
    
    
    @key.setter
    def key( self, value: str ):
        del self.__header_collection[ self.__key ]
        self.__key = value
        self.__header_collection[ self.__key ] = self
    
    
    @property
    def text( self ) -> str:
        """
        Read-write property that represents the actual header text.
        By default this is the same as the `key`.
        If this is changed, the underlying `ProgressiveCsvWriter` will be flagged as `needs_rewrite`.
        """
        return self.__text
    
    
    @text.setter
    def text( self, value: str ):
        self.__text = value
        self.__owner.needs_rewrite = True
    
    
    @property
    def index( self ) -> int:
        """
        Index of the header.
        This may not be changed.
        """
        return self.__index
    
    
    def __str__( self ):
        """
        OVERRIDE 
        """
        return "{}@{}".format( self.__key, self.__index )
    
    
    def __repr__( self ):
        """
        OVERRIDE
        """
        return "ProgressiveCsvHeader( {}, {}, {} )".format( repr( self.__owner ), repr( self.key ), repr( self.index ) )


DHeaderChanger = Callable[ [ ProgressiveCsvHeader ], None ]
"""
Called to modify headers before or after reads.
:param 0: Header being written or read.
:return:  The return value is unused.
"""


class ProgressiveCsvWriter:
    """
    Used to write CSV files progressively - that is, allowing the headers to be modified on the fly.
    
    * Headers are held "in waiting" during writing
        * When the file is closed, any additional or renamed headers are written and rows with missing columns are
          padded with the specified `default`
    * To avoid use of incomplete data, by default the file is renamed to a temporary during use
    """
    
    
    def __init__( self, 
                  file_name: str,
                  dialect = "excel",
                  default: str = "",
                  on_read: Optional[ DHeaderChanger ] = None,
                  on_write: Optional[ DHeaderChanger ] = None,
                  remove_temp: bool = True ):
        """
        CONSTRUCTOR.
        :param file_name:    File to load/save
        :param dialect:      CSV dialect. See csv module.
        :param default:      Value used to pad cells for which a value has not been provided.
        :param on_read:      Called when reading or creating headers for the first time. See `DHeaderChanger`.
        :param on_write:     Called before writing headers to disk. Only called if headers changed. See `DHeaderChanger`.
        """
        self.__original_file_name = file_name
        self.__temporary_file_name = file_name + ".~prtmp"
        
        # Remove any temporary file in the way
        if path.isfile( self.__temporary_file_name ):
            if remove_temp:
                os.remove( self.__temporary_file_name )
            else:
                raise FileExistsError( "Temporary file already exists. This may indicate a previous run failed. If so, the temporary file cannot be recovered because the headers were lost. Please remove the temporary file at «{}» and try again.".format( self.__temporary_file_name ) )
        
        # Work with the temporary file
        if path.isfile( self.__original_file_name ):
            os.rename( self.__original_file_name, self.__temporary_file_name )
        
        # General settings
        self.__dialect = dialect
        self.__default = default
        self.__needs_rewrite = False
        self.__on_read = on_read
        self.__on_write = on_write
        self.__headers = OrderedDict()  # type: Dict[str, ProgressiveCsvHeader]
        needs_header_line = not self.__read_headers()
        self.__file_out = open( self.__temporary_file_name, "a" )
        self.__writer = csv.writer( self.__file_out, dialect = self.__dialect )
        self.__headers_proxy = ReadonlyDictProxy( self.__headers )
        
        if needs_header_line:
            self.__writer.writerow( [ "HEADER_PLACEHOLDER" ] )
            
    def __enter__(self):
        """
        OVERRIDE 
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        OVERRIDE 
        """
        self.close()
    
    
    @property
    def needs_rewrite( self ) -> bool:
        """
        Read-write property that when `True` indicates that the file will be rewritten before it is closed.
        Note that externally the value may only be set to `True`, not `False`. 
        """
        return self.__needs_rewrite
    
    
    @needs_rewrite.setter
    def needs_rewrite( self, value: bool ):
        value = bool( value )
        
        if not value:
            raise ValueError( "Cannot clear the `needs_rewrite` flag externally." )
        
        self.__needs_rewrite = value
    
    
    @property
    def headers( self ) -> Dict[ str, ProgressiveCsvHeader ]:
        """
        Read-only property that allows the headers to be accessed.
        """
        # noinspection PyTypeChecker
        return self.__headers_proxy
    
    
    def __repr__( self ):
        """
        OVERRIDE 
        """
        return "ProgressiveCsvWriter( {}, ... )".format( repr( self.__original_file_name ) )
    
    
    def close( self ):
        """
        Closes the stream, rewriting the file with the new headers if necessary.
        You can query `needs_rewrite` to determine if a rewrite will be required.
        """
        
        # Close the stream
        self.__file_out.close()
        
        # Rewrite the file with the new headers, if required
        if self.__needs_rewrite:
            tmp2_file_name = self.__original_file_name + ".~phtmp"
            
            with open( self.__temporary_file_name, "r" ) as file_in:
                csv_reader = csv.reader( file_in, dialect = self.__dialect )
                
                with open( tmp2_file_name, "w" ) as file_out:
                    csv_writer = csv.writer( file_out, dialect = self.__dialect )
                    
                    # Skip original headers, write new headers
                    _ = next( csv_reader )
                    csv_writer.writerow( header.text for header in self.__headers.values() )
                    
                    num_headers = len( self.__headers )
                    
                    # Write rows, padding with the default value as necessary
                    for row in csv_reader:
                        extra = num_headers - len( row )
                        
                        if extra:
                            row += [ self.__default ] * extra
                        
                        csv_writer.writerow( row )
            
            # Replace our temporary file with the rewritten version
            os.remove( self.__temporary_file_name )
            os.rename( tmp2_file_name, self.__temporary_file_name )
        
        # Replace our original file with the temporary version
        if path.isfile( self.__original_file_name ):
            raise FileExistsError( "The CSV file at «{}» was modified externally and cannot be written.".format( self.__original_file_name ) )
        
        os.rename( self.__temporary_file_name, self.__original_file_name )
        
        # Shut down the writer
        self.__writer = None
        self.__file_out = None
    
    
    def __read_headers( self ) -> bool:
        """
        Internally function that reads the headers if the file already exists.
        """
        if not path.isfile( self.__temporary_file_name ):
            return False
        
        with open( self.__temporary_file_name, "r" ) as file_in:
            csv_reader = csv.reader( file_in, dialect = self.__dialect )
            
            try:
                headers = next( csv_reader )
            except StopIteration:
                return False
            
            for header in headers:
                header = ProgressiveCsvHeader( self, header, len( self.__headers ), self.__headers )
                
                if self.__on_read:
                    self.__on_read( header )
        
        return True
    
    
    def write_row( self, contents: Dict[ str, object ] ):
        """
        Writes a row.
        :param contents:    Row contents, as a dictionary of header-key to value.
                            Missing keys will be replaced by the `default` value specified during construction.
                            New keys will result in a call to `append_header`.
        :return: 
        """
        if self.__writer is None:
            raise ValueError( "Cannot write to a closed stream «{}».".format( self ) )
        
        row = [ self.__default ] * len( self.__headers )
        
        for k, v in contents.items():
            header = self.__headers.get( k, None )
            
            if header is None:
                self.append_header( k )
                row.append( str(v) )
            else:
                row[ header.index ] = v
        
        self.__writer.writerow( row )
    
    
    def append_header( self, header: str ) -> ProgressiveCsvHeader:
        """
        Adds a new header.
        :param header: key of the new header. If you set `on_read` in the constructor, this will be called.
        :return: The new header. 
        """
        header = ProgressiveCsvHeader( self, header, len( self.__headers ), self.__headers )
        self.__needs_rewrite = True
        
        if self.__on_read:
            self.__on_read( header )
        
        return header
