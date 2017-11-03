"""
Contains functions for meddling with parcels (merging them, checking them, removing duplicates, etc).
"""

import csv
import os
import shutil

from typing import Tuple, List, Optional

from os import path
from uuid import uuid4

from intermake import command, constants as mconstants, MENV
from intermake.engine.environment import MCMD
from intermake.plugins.visibilities import VisibilityClass

from neocommand.data import constants
from mhelper import file_helper as FileHelper
from neocommand.database.endpoints import NeoCsvFolderEndpoint
from neocommand.helpers.neo_csv_helper import NeoCsvFilename

__mcmd_folder_name__ = "parcels"

PARCEL_EXTRA = VisibilityClass( name = "parcel_extra",
                                default = False,
                                comment = "Advanced parcel commands." )

@command(visibility = PARCEL_EXTRA)
def parcel_remove_duplicates( input: NeoCsvFolderEndpoint, output: NeoCsvFolderEndpoint ) -> int:
    """
    Applies `neocsv_remove_duplicates` to all CSVs in folder. 
    :param input: Directory to process 
    :param output: Output folder name 
    :return: 
    """
    file_names = os.listdir( input.full_path() )
    
    file_names = list( [ x for x in file_names if x.lower().endswith( constants.EXT_B42CSV ) ] )
    
    for file_name in MCMD.iterate( file_names, "Removing duplicates" ):
        in_file_name = os.path.join( input.full_path(), file_name )
        
        if output == input:
            out_file_name = in_file_name
        else:
            out_file_name = os.path.join( output.full_path(), file_name )
        
        parcel_remove_duplicates_file( NeoCsvFilename.construct_from_file( in_file_name ), NeoCsvFilename.construct_from_file( out_file_name ) )
    
    return len( file_names )


@command(visibility = PARCEL_EXTRA)
def parcel_remove_duplicates_file( input: NeoCsvFilename, output: Optional[ NeoCsvFilename ] = None ):
    """
    Removes the duplicates from a CSV file

    :param input: Input file
    :param output: Output file, (if None or matches file_name) a temporary file will be used and the original file replaced on completion
    :return: Tuple of unique keys and duplicate keys
    """
    
    pk_column = -1
    keys = { }
    
    num_duplicates = 0
    
    if output is None or (output.filename == input.filename):
        replace_original = True
        out_file_name_using = output.filename or (input.filename + "-duplicates-removed.tmp")
    else:
        replace_original = False
        out_file_name_using = output.filename
    
    with open( out_file_name_using, "w" ) as out_file:
        writer = csv.writer( out_file )
        
        with MCMD.action( "Removing duplicates" ) as a:
            with open( input.filename, "r" ) as in_file:
                reader = csv.reader( in_file )
                
                for columns in reader:
                    a.increment()
                    
                    if pk_column == -1:
                        # Not got headers yet!
                        for i, h in enumerate( columns ):
                            if h.startswith( constants.PRIMARY_KEY_DECORATED_NAME ):
                                pk_column = i
                                break
                        
                        if pk_column == -1:
                            raise ValueError( "Could not find primary key column in {0}".format( input ) )
                    else:
                        primary_key = columns[ pk_column ]
                        crc = __crc32( columns )
                        
                        if primary_key in keys:
                            # Duplicate :!
                            num_duplicates += 1
                            
                            crc2 = keys[ primary_key ]
                            
                            if crc != crc2:
                                raise ValueError( "CSV duplicate has different CRC: {0} around {1}".format( primary_key, ", ".join( columns ) ) )
                            
                            continue  # don't write the duplicate
                        else:
                            keys[ primary_key ] = crc
                    
                    writer.writerow( columns )
    
    if replace_original:
        os.replace( out_file_name_using, input.filename )
    
    return len( keys ), num_duplicates


@command(visibility = PARCEL_EXTRA)
def parcel_merge( left: NeoCsvFolderEndpoint, right: NeoCsvFolderEndpoint, output: NeoCsvFolderEndpoint, test: bool = False ) -> Tuple[ List[ str ], List[ str ], List[ str ] ]:
    """
    Merges the CSVs in two directories
    :param test: When set no changes will actually be performed on disk, but the results of the function will still be the same 
    :param left: Top dir
    :param right: Bottom dir
    :param output: Resultant DIR
        If this doesn't exist then it will be created.
        This can be dir_name_a or dir_name_b, in which case destination files will overwrite source files - see merge_csvs.
    :return: List of A files, list of B files, list of merged (A+B) files
    """
    
    left_files = [ ]
    right_files = [ ]
    merged_files = [ ]
    
    file_names = set( os.listdir( left.full_path() ) )
    # noinspection PyTypeChecker
    file_names.update( os.listdir( right.full_path() ) )
    
    file_names = [ x for x in file_names if FileHelper.get_extension( x ) == constants.EXT_B42CSV ]
    
    for file_name in MCMD.iterate( "Iterating files", file_names ):
        left__file_name = os.path.join( left.full_path(), file_name )
        right_file_name = os.path.join( right.full_path(), file_name )
        out___file_name = os.path.join( output.full_path(), file_name )
        left__exists = os.path.isfile( left__file_name )
        right_exists = os.path.isfile( right_file_name )
        
        if left__exists:
            if right_exists:
                with MCMD.action( "Merging from A+B: " + file_name ):
                    if not test:
                        parcel_merge_file( MCMD, NeoCsvFilename.construct_from_file( left__file_name ), NeoCsvFilename.construct_from_file( right_file_name ), NeoCsvFilename.construct_from_file( out___file_name ) )
                    merged_files.append( file_name )
            else:
                with MCMD.action( "Copying from A: " + file_name ):
                    if left__file_name != out___file_name:
                        if not test:
                            shutil.copy( left__file_name, out___file_name )
                    left_files.append( file_name )
        elif right_exists:
            with MCMD.action( "Copying from B: " + file_name ):
                if right_file_name != out___file_name:
                    if not test:
                        shutil.copy( right_file_name, out___file_name )
                right_files.append( file_name )
        else:
            raise ValueError( "File {0} found initially but now does not exist.".format( file_name ) )
    
    return left_files, right_files, merged_files


@command(visibility = PARCEL_EXTRA)
def parcel_merge_file( file_name_a: NeoCsvFilename, file_name_b: NeoCsvFilename, file_name_out: NeoCsvFilename ) -> Tuple[ int, int ]:
    """
    Merges two CSVs
    Accounts for header order

    :param file_name_a: Top file
    :param file_name_b: Bottom file
    :param file_name_out: Resultant file. This can be file_name_a or file_name_b if the filenames match exactly (a temporary file will be used during the operation).
    :return: File a length, File b length
    """
    
    a_lines = 0
    b_lines = 0
    
    temp_dest = None
    
    if file_name_out == file_name_a or file_name_out == file_name_b:
        temp_dest = file_name_out
        file_name_out = path.join(MENV.local_data.local_folder(mconstants.FOLDER_TEMPORARY), "temporary-{}.tmp".format(uuid4()))
    
    with open( file_name_out, "w" ) as file_out:
        writer = csv.writer( file_out )
        
        with MCMD.action( "Iterating file A: " + file_name_a.filename ) as action:
            with open( file_name_a.filename, "r" ) as file_a:
                reader = csv.reader( file_a )
                
                a_headers = next( reader )
                writer.writerow( a_headers )
                
                for row in reader:
                    action.increment()
                    writer.writerow( row )
                    a_lines += 1
        
        row_len = len( a_headers )
        
        with MCMD.action(  "Iterating file B: " + file_name_a.filename ) as action:
            with open( file_name_b.filename, "r" ) as file_b:
                reader = csv.reader( file_b )
                
                b_headers = next( reader )
                
                relocate = [ -1 ] * row_len
                
                for a_index, a_header in enumerate( a_headers ):
                    if a_header not in b_headers:
                        raise KeyError( "The key «{0}» is in file «{1}» but not in file «{2}» so they cannot be merged. Please check your data and rectify the problem before continuing.".format( a_header, file_name_a, file_name_b ) )
                    
                    b_index = b_headers.index( a_header )
                    
                    relocate[ b_index ] = a_index
                
                for row in reader:
                    action.increment()
                    new_row = [ -1 ] * row_len
                    
                    for i in range( row_len ):
                        new_row[ relocate[ i ] ] = row[ i ]
                    
                    writer.writerow( new_row )
                    b_lines += 1
    
    if temp_dest:
        os.replace( file_name_out, temp_dest )
    
    return a_lines, b_lines


def __crc32( columns ):
    import binascii
    return binascii.crc32( ",".join( columns ).encode( "utf-8" ) )
