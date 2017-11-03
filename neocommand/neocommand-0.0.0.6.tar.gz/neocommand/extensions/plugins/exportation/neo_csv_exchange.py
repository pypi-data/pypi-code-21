"""
This module contains convenience Plugins for sending and receiving data from a remote host.

It is only useful if the Neo4j database is actually stored a remote host! 
"""
import os
from typing import List

from colorama import Style

from intermake.datastore.local_data import LocalData
from intermake.engine.environment import MCMD
from mhelper import file_helper as FileHelper

from intermake import command

from neocommand.data import constants
from neocommand.data.core import CORE
from neocommand.database.endpoints import NeoCsvFolderEndpoint

__mcmd_folder_name__ = "parcels"

@command(  )
def parcel_send( parcel: NeoCsvFolderEndpoint, rezip: bool = True, clean: bool = True, pause: bool = False ):
    """
    Sends an import parcel to the server via SSH (scp)
    
    [1] Note that any files deleted or overwritten are sent to the user's Recycle Bin
    
    :param pause:   Pauses after zipping, before SCP (in case SCP requires password on a short timeout).
    :param clean:   When `True` the ZIP file will be deleted after the exchange [1]
    :param parcel:  Name of the parcel
    :param rezip:   When `True`, the zip file will always be recreated, even if it already exists [1]
    """
    
    folder_name = parcel.full_path()
    
    SEND_FILE = "scp {0} {1}@{2}:{3}"
    
    zipped_file = __zip( folder_name, not rezip )
    
    os.chdir( FileHelper.get_directory( zipped_file ) )
    
    zipped_file_short = FileHelper.get_filename( zipped_file )
    
    remote_file_name = os.path.join( __raw_receiver_directory(), zipped_file_short )
    
    if not CORE.settings.ssh_user:
        raise ValueError( "Missing SSH username. Please define in settings." )
    
    if not CORE.settings.ssh_host:
        raise ValueError( "Missing SSH host. Please define in settings." )
    
    if pause:
        if not MCMD.question("Ready for SCP, continue?"):
            MCMD.print("User chose to abort. Note that the ZIP file at «{}» has not been deleted.".format(zipped_file))
            return
    
    with MCMD.action( "Invoking SCP (see console output for progress and if logon required)" ):
        command = SEND_FILE.format( zipped_file_short, CORE.settings.ssh_user, CORE.settings.ssh_host, remote_file_name )
        os.system( command )
    
    if clean:
        FileHelper.recycle_file( zipped_file )


@command()
def parcel_receive( test: bool = False ):
    """
    Looks for any received parcels and unpacks them
    * Use `received` to list options.
    
    :param test: When `True` received parcels will be listed but not unpacked.
    :return: Nothing 
    """
    
    files = __list_unpack()
    
    if test:
        for targz in files:
            MCMD.print( "+ " + constants.COL_ITEM + FileHelper.get_filename_without_extension( targz ) + Style.RESET_ALL )
            return
    
    result = [ ]
    
    with MCMD.action( "Unpacking files", len( files ) )as a:
        for file_name in files:
            a.increment()
            
            renamed_zip = os.path.join( CORE.endpoint_manager.user_endpoints_default_folder(), FileHelper.get_filename( file_name ) )
            
            if not os.path.isfile( file_name ):
                raise FileNotFoundError( "File not found: " + file_name )
            
            os.rename( file_name, renamed_zip )
            
            unzipped_dir = __unzip( renamed_zip )
            
            # If all went well we now have a directory (new_folder) containing another directory, possibly with the same name
            x = os.listdir( unzipped_dir )
            
            if len( x ) != 1:
                raise FileExistsError( "Expected unzipped directory «{0}» to contain one folder, but it doesn't, it contains {1}.".format( unzipped_dir, len( x ) ) )
            
            tall_directory = os.path.join( unzipped_dir, x[ 0 ] )
            
            for xx in os.listdir( tall_directory ):
                old = os.path.join( tall_directory, xx )
                new = os.path.join( unzipped_dir, xx )
                os.rename( old, new )
            
            # Delete the zip
            FileHelper.recycle_file( renamed_zip )
            
            result.append( unzipped_dir )
    
    return result


def __zip( folder_name: str, skip_if_exists = False ) -> str:
    """
    Zips the folder
    Any existing zips will be overwritten

    :param folder_name: Folder name
    :param skip_if_exists: When true, if the ZIP file already exists then the function will return immediately
    :return: Name of folder
    """
    TARGZ_FILE = 'tar -zcvf "{0}" "{1}"'
    
    os.chdir( FileHelper.get_directory( folder_name ) )
    
    out_file_name = folder_name + constants.EXT_B42ZIP
    
    if os.path.isfile( out_file_name ):
        if skip_if_exists:
            return out_file_name
        
        FileHelper.recycle_file( out_file_name )
    
    with MCMD.action( "Invoking TAR (see console output for progress details)" ):
        command = TARGZ_FILE.format( FileHelper.get_filename( out_file_name ), FileHelper.get_filename( folder_name ) )
        os.system( command )
    
    return out_file_name


def __unzip( file_name: str ) -> str:
    """
    Unzips a file

    Since we can't be sure what's inside the zip we always unzip to a new folder (with the same name as the zip)

    This means that eggs.zip usually unzips to a file structure like eggs/eggs/spam...

    But if eggs.zip has been renamed by the user it might unzip to eggs/beans/spam... or a tar-bomb will unzip to eggs/spam...

    The unpack() method takes care of this by moving eggs/eggs/spam... or eggs/beans/spam... back into eggs/spam... .
    """
    UNTARGZ_FILE = 'tar -zxvf "{0}" -C "{1}"'
    
    new_folder = FileHelper.get_full_filename_without_extension( file_name )
    
    if os.path.exists( new_folder ):
        raise FileExistsError( "Unzipping directory «{0}» already exists.".format( new_folder ) )
    
    FileHelper.create_directory( new_folder )
    
    command = UNTARGZ_FILE.format( file_name, new_folder )
    
    with MCMD.action( "Invoking UNTAR (see console output for progress details)" ):
        os.system( command )
    
    return new_folder


def __is_zipped( folder_name: str ) -> bool:
    """
    Determines if the specified folder is already zipped
    """
    out_file_name = folder_name + constants.EXT_B42ZIP
    
    return os.path.isfile( out_file_name )


def __receiver_directory():
    return os.path.expanduser( __raw_receiver_directory() )


def __raw_receiver_directory():
    return os.path.join( LocalData.default_workspace(), "received" )


def __list_unpack() -> List[ str ]:
    """
    Lists files ready for unpacking
    """
    r = __receiver_directory()
    
    return list( [ os.path.join( r, x ) for x in os.listdir( r ) if x.endswith( constants.EXT_B42ZIP ) ] )
