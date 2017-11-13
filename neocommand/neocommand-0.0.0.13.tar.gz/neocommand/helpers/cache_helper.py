"""
Manages a set of caches that plugins can use to:

    1. Save data in case of the need to resume later
    2. Save data in case multiple plugins need to make use of it
    3. Transfer data from one long running thread or process to another
        - Have one thread be responsible for calculating the data and the rest wait on it
        - Have multiple threads responsible for calculating the data and one wait on them to collate it
         
Usage - checking a cache:
    ```
    my_data = load_cache_binary_dict( "my_cache" )
    
    if my_data is None:
        my_data = . . . 
        save_cache_binary_dict( "my_cache", my_data )
    ```

Usage - waiting on one thread
    ```
    my_data = load_cache_binary_dict( "my_cache", single = True )
    
    if my_data is None:
        assert MCMD.is_first_thread
        . . .
    ```
    
Usage - having one thread collate results
    ```
    save_cache_binary_dict( ["my_cache", MCMD.thread_index ], my_thread_data )
    ```
"""
import os
from os import path
from time import sleep
from typing import Optional, Any, Tuple, Type, TypeVar, Sized

import numpy
from bitarray import bitarray

from mhelper import MEnum
from intermake import constants as mconstants
from intermake.engine.environment import MENV, MCMD

from mhelper import exception_helper, SwitchError, file_helper, string_helper, io_helper
from neocommand.data import constants





#region Cache enums

T = TypeVar("T")


class EFormat( MEnum ):
    """
    Formats for saving data to caches. Also controls the file extension.
    
    `BINARY_B42`
        Nothing special, just pickle the data into a binary thingy.
        
    `BINARY_DICT`
        Same as `BINARY_B42` with an added check that this is a `dict`.
        
    `NUMPY_NPZ`
        Use Numpy's serialisation, for Numpy objects, namely `ndarray`.
    
    `BITARRAY`
        Bit array. `bitarray`.
        
    `JSON`
        ¡REMOVED! Don't reimplement this, it's far too slow.
    """
    BINARY_B42 = 0
    BINARY_DICT = 1
    NUMPY_NPZ = 2
    BITARRAY = 3
    BINARY_SET = 4
    BINARY_TUPLE = 5

class ECache( MEnum ):
    """
    Determines how caches are managed. 
    
    :data DEFAULT:      The value in CORE.settings is used (use the `set` command from the CLI or open the settings page from the GUI).
                        If this value is also `DEFAULT` then `LOAD` is used.

    :data LOAD:         Data is loaded from disk.
                        If it doesn't exist an error will be generated.
                        * Use this option to avoid accidentally using the wrong parameters when you know the data is available on disk.
        
    :data OVERWRITE:    Data is created.
                        It is saved to disk upon completion.
                        If the data already exists on disk it will be overwritten.
                        * Use this option when you know the data on disk to be obsolete or incorrect. 
        
    :data SELECT:       Data is loaded from disk if possible, otherwise it will be created.
                        If created, it is saved to disk upon completion.
                        * Use this option when you don't know whether the data is already available or not.
        
    :data NOSAVE:       Same as `OVERWRITE` but data is never written to disk.
                        * Use this option if you never intend to cache data, this saves time not having to write the cache to disk.
    """
    DEFAULT = 0
    LOAD = 1
    OVERWRITE = 2
    SELECT = 3
    NOSAVE = 4
    ASK = 5
    
#endregion


#region Cache decorators

def cache_result( format = EFormat.BINARY_B42, folder = "general" ):
    """
    Decorator that instructs a function to cache its result (in the `general` cache folder)
    
    `kwargs` are not processed and should not be used.
    
    :param format: The format to cache the data as 
    :param folder: The folder to cache into
    :return: The cached, or new, result 
    """
    
    
    def provider( orig_function ):
        def new_function( *args ):
            extra_args = list( args )
            cache_name = [ folder, orig_function.__name__ ] + extra_args
            
            cached = load_cache(  cache_name, format = format, mode = ECache.SELECT )
            
            if cached is not None:
                return cached
            
            cached = orig_function( *args )
            
            save_cache(  cache_name, format = format, mode = ECache.SELECT, data = cached )
            
            return cached
        
        
        return new_function
    
    
    return provider

#endregion


#region Load-cache wrappers
def load_cache_binary_dict(  name: object, **kwargs ) -> Optional[ dict ]:
    """
    Loads a `dict`. See `load_cache` for details.
    """
    return load_cache(  name, EFormat.BINARY_B42, **kwargs )


def load_cache_object(  name: object, type_ : Type[T], **kwargs ) -> Optional[ T ]:
    result = load_cache_binary_b42( name, **kwargs)
    exception_helper.assert_instance_or_none("result", result, type_)
    return result

def load_cache_binary_b42( name: object, **kwargs ) -> Optional[ object ]:
    """
    Loads a picklable `object` (use with care). See `load_cache` for details.
    """
    return load_cache(  name, EFormat.BINARY_B42, **kwargs )

def load_cache_set(  name: object, **kwargs ) -> Optional[ set ]:
    """
    Loads a picklable `object` (use with care). See `load_cache` for details.
    """
    return load_cache(  name, EFormat.BINARY_SET, **kwargs )


def load_cache_numpy_npz(  name: object, **kwargs ) -> Optional[ numpy.ndarray ]:
    """
    Loads an `ndarray`. See `load_cache` for details.
    """
    return load_cache(  name, EFormat.NUMPY_NPZ, **kwargs )

def load_cache_tuple(  name: object, count : int, **kwargs ) -> Tuple[ Optional[Any] ]:
    """
    Loads an `ndarray`. See `load_cache` for details.
    """
    values = load_cache(  name, EFormat.BINARY_TUPLE, **kwargs )
    
    if values is None:
        values = tuple([None] * count)
        
    assert isinstance(values, tuple)
    assert len(values) == count
    return values
    


def load_cache_bit_array(  name: object, length : int, **kwargs ) -> Optional[ bitarray ]:
    """
    Loads a `bitarray`. See `load_cache` for details.
    """
    result : Optional[Sized] = load_cache(  name, EFormat.BITARRAY, **kwargs )
    
    if result is not None:
        if len(result) < length:
            raise ValueError("The cached result was retrieved but the bitarray returned is shorter than expected, having a length of {} instead of {}.".format(len(result), length))
        
        if len(result) >= length + 8:
            raise ValueError("The cached result was retrieved but the bitarray returned is longer than expected, having a length of {} instead of {}.".format(len(result), length))
        
    return result
    
#endregion


#region Save-cache wrappers
def save_cache_binary_dict(  name: object, value: dict ):
    """
    Saves a `dict`. See `save_cache` for details.
    """
    save_cache(  name, EFormat.BINARY_B42, value )
    
def save_cache_set(  name: object, value: set ):
    """
    Saves a `dict`. See `save_cache` for details.
    """
    save_cache(  name, EFormat.BINARY_SET, value )


def save_cache_binary_b42(  name: object, value: object ):
    """
    Saves a picklable `object`. See `save_cache` for details.
    """
    save_cache(  name, EFormat.BINARY_B42, value )


def save_cache_numpy_npz(  name: object, value: numpy.ndarray ):
    """
    Saves an `ndarray`. See `save_cache` for details.
    """
    save_cache(  name, EFormat.NUMPY_NPZ, value )
    
def save_cache_tuple(  name: object, values : tuple ):
    """
    Saves an `ndarray`. See `save_cache` for details.
    """
    assert isinstance(values, tuple)
    save_cache(  name, EFormat.BINARY_TUPLE, values )


def save_cache_bit_array(  name: object, value: bitarray ):
    """
    Saves a `bitarray`. See `save_cache` for details.
    """
    save_cache(  name, EFormat.BITARRAY, value )
#endregion


#region Wait flags

def wait_for_flag(  name: object ) -> None:
    """
    Waits until the specified flag is true.
    
    Right now flags are always file flags, waited on by polling the file-system every 10 seconds.
    
    :param name:    Flag name 
    :return:        Nothing 
    """
    # This works (although it still isn't great) for long multiprocess operations on a compute cluster.
    # however, it is overkill for operations on the same machine. It also introduces an unnecessary delay in short-running tasks.
    # TODO: Improve this. May need to ask the host.
    #       Where this is used, files such as caches may have been used to transfer data. These need fixing too.
    
    file_name = __get_cache_file_name( name ) + ".flag"
    
    MCMD.print("Waiting on flag: {}".format(file_name) )
    
    with MCMD.action("Waiting for signal: {}".format(file_name)) as action:
        while not path.isfile(file_name):
            action.still_alive()
            sleep(10)
            

def set_flag( name: object, value : bool) -> None:
    """
    Sets a "flag". "flags" are by default `False`.
    
    See comments in `wait_for_flag`.
    
    :param name:    Name of flag to set 
    :param value:   Value to set the flag to. 
    :return:        Nothing. 
    """
    file_name = __get_cache_file_name( name ) + ".flag"
    
    if value:
        MCMD.print("Setting flag: {}".format(file_name) )
        file_helper.write_all_text(file_name, "1")
    else:
        MCMD.print("Removing flag: {}".format(file_name) )
        if path.isfile(file_name):
            os.remove(file_name)

#endregion


#region Cache operations

def load_cache( name   : object,
                format : EFormat,
                mode   : ECache                   = ECache.DEFAULT,
                wait   : bool                     = False,
                test   : bool                     = False,
                single : bool                     = False ) -> Optional[ object ]:
    """
    Loads a cache file, if it exists, else returns `None`.
    
    :param name:            See the `__get_cache_file_name` function. 
    :param format:          See the `__get_cache_file_name` function. Format is based on file extension if not specified. 
    :param mode:            When `ECache.LOAD` an error will be raised if the result is `None`. When `ECache.OVERWRITE` or `ECache.NOSAVE` the result will always be `None`. 
    :param single:          Single-worker mode - sets `wait` to `True` when this is not the first process of a multi-process array.
    :param wait:            When `True` the system will wait for the cache to become available. Used if another process or thread is calculating the workload.
                            TODO: Even on multi-threaded (as opposed to multi-cored) we go through the disk - this is unnecessary.
    :param test:            When `True` the result will not be loaded, instead `True` will be returned if the cache exists (`None` will be returned otherwise - (*not* `False`) ).
    :return:                The cached object.
                            Or `True` if the cache exists and the `test` parameter is set.
                            `None` if the cached result is not available.
    """
    if single:
        wait = MCMD.is_secondary_thread
        
    #
    # Check against obsolete calls which had a different signature
    #
    assert isinstance( format, EFormat )
    
    #
    # Get the mode from the system settings
    #
    mode = __translate_cache_mode( mode )
    
    if mode == ECache.OVERWRITE or mode == ECache.NOSAVE:
        return None
    
    #
    # Get the name of the file and its guard
    #
    file_name = __get_cache_file_name( name, format )
    guard_file_name = file_name + ".guard"
    description = path.join( file_helper.get_filename( file_helper.get_directory( file_name ) ), file_helper.get_filename( file_name ) )
    
    #
    # Wait for the cache to become available
    #
    if wait and not path.isfile(guard_file_name):
        with MCMD.action("Waiting for cache: {}".format(description)) as action:
            while not path.isfile(guard_file_name):
                action.still_alive()
                sleep(10)
    
    #
    # See if the guard lets us pass
    #
    if not path.isfile( guard_file_name ):
        MCMD.print( "Cached result not available: " + description )
        __handle_missing_cache( mode, file_name)
        return None
    
    #
    # Return a success (if testing)
    #
    if test:
        return True

    MCMD.print( "Cached result is available: " + description )
    size_text = string_helper.size_to_string( file_helper.file_size( file_name ) )
        
    #
    # Load the cache
    #
    with MCMD.action( "Loading cache: {} «{}»".format(size_text, description) ):
        result = None # for PyCharm
        
        try:
            if format == EFormat.BINARY_B42:
                result = io_helper.load_binary( file_name )
                assert result is not None
            elif format == EFormat.BINARY_DICT:
                result = io_helper.load_binary( file_name )
                exception_helper.assert_instance_or_none("result", result, dict)
            elif format == EFormat.NUMPY_NPZ:
                result = io_helper.load_npz( file_name )
                exception_helper.assert_instance_or_none("result", result, numpy.ndarray)
            elif format == EFormat.BITARRAY:
                result = io_helper.load_bitarray( file_name )
                exception_helper.assert_instance_or_none("result", result, bitarray)
            elif format == EFormat.BINARY_SET:
                result = io_helper.load_binary( file_name )
                exception_helper.assert_instance_or_none("result", result, set)
            elif format == EFormat.BINARY_TUPLE:
                result = io_helper.load_binary( file_name )
                exception_helper.assert_instance_or_none("result", result, tuple)
            else:
                raise SwitchError( "file type for load_cache", name )
        except Exception as ex:
            raise ValueError("Failed to load the cache due to an error. Please remove the cache file at «{}».".format(file_name) ) from ex
        
        if result is None:
            raise ValueError( "The cache was loaded but its content is `None`. Please remove the cache file at «{}».".format(file_name) )
        
    MCMD.print( "Cache load succeeded: " + description )
    
    return result


def save_cache(  name: object, format: EFormat, data: Any, mode: ECache = ECache.DEFAULT ) -> None:
    """
    Saves a cache file.
    
    :param mode: When `ECache.NOSAVE` this function does nothing. 
    :param name: See the `__get_cache_file_name` function. 
    :param format: See the `__get_cache_file_name` function.
    :param data: Data to cache.
    """
    mode = __translate_cache_mode( mode )
    
    if mode == ECache.NOSAVE:
        return
    
    file_name = __get_cache_file_name( name, format )
    guard_file_name = file_name + ".guard"
    
    if path.isfile(guard_file_name):
        os.remove(guard_file_name)
        
    if path.isfile(file_name):
        os.remove(file_name)
        
    assert not path.exists(file_name), file_name
    assert not path.exists(guard_file_name), guard_file_name
    
    description = path.join( file_helper.get_filename_without_extension( file_helper.get_directory( file_name ) ), file_helper.get_filename_without_extension( file_name ) )
    
    with MCMD.action( "Saving {} cache: «{}»".format(format, description) ):
        if format == EFormat.BINARY_B42:
            exception_helper.assert_instance("data", data, object)
            io_helper.save_binary( file_name, data )
        elif format == EFormat.BINARY_DICT:
            exception_helper.assert_instance("data", data, dict)
            io_helper.save_binary( file_name, data )
        elif format == EFormat.NUMPY_NPZ:
            exception_helper.assert_instance("data", data, numpy.ndarray)
            io_helper.save_npz( file_name, data )
        elif format == EFormat.BITARRAY:
            exception_helper.assert_instance("data", data, bitarray)
            io_helper.save_bitarray( file_name, data )
        elif format == EFormat.BINARY_SET:
            exception_helper.assert_instance("data", data, set)
            io_helper.save_binary( file_name, data )
        elif format == EFormat.BINARY_TUPLE:
            exception_helper.assert_instance("data", data, tuple)
            io_helper.save_binary( file_name, data )
        else:
            raise SwitchError( "file type for save_cache", name )
        
    #
    # Write the guard
    # - The guard makes sure we don't load data in the case where the file isn't fully
    #   written (either from another thread or if the program is terminated abruptly
    #   and restarted)
    #
    file_helper.write_all_text( guard_file_name, "file="+guard_file_name + "\ntype=" + type( data ).__name__ )


# noinspection PyUnusedLocal
def delete_cache( name: object, format: EFormat):
    """
    Deletes a cache file, if it exists
    :param name:    See the `__get_cache_file_name` function. 
    :param format:  See the `__get_cache_file_name` function.
    :return: Nothing
    """
    file_name = __get_cache_file_name( name, format )
    
    if path.isfile(file_name):
        file_helper.recycle_file(file_name)

#endregion


#region Private


__session_cache_skip = False


def __cache_folder_name( local_folder ):
    """
    Gets the folder where this plugin stores its data.
    """
    folder_name = path.join(MENV.local_data.local_folder(mconstants.FOLDER_SETTINGS), local_folder)
    file_helper.create_directory(folder_name)
    return folder_name



def __get_cache_file_name( name: object, format: EFormat = None ):
    """
    Gets the full path of a local cache-file for this plugin.
    
    :param name: Identifier of the file, as a list. The first element should be the folder, which can optionally contain subfolders, delimited with '/'. 
    :param format: Format of the file, specified as an extension with or without the leading dot `.`. 
    :return: The full path to the file. 
    """
    folder = None
    
    if isinstance( name, list ):
        folder = name[ 0 ]
        if len( name ) == 1:
            cache_name = "data"
        else:
            cache_name = ",".join( str( x ) for x in name )
    else:
        cache_name = str( name )
    
    for x in " /\\:*?<>'\"":
        cache_name = cache_name.replace( x, "_" )
        
    if format is None:
        ext = ""
    elif format == EFormat.BINARY_B42:
        ext = ".b42-obj"
    elif format == EFormat.BINARY_DICT:
        ext = ".b42-dict"
    elif format == EFormat.NUMPY_NPZ:
        ext = constants.EXT_NPZ
    elif format == EFormat.BITARRAY:
        ext = ".bitarray"
    elif format == EFormat.BINARY_SET:
        ext = ".b42-set"
    elif format == EFormat.BINARY_TUPLE:
        ext = ".b42-tuple"
    else:
        raise SwitchError("format", format)
    
    cache_name += ext
    
    return path.join( __cache_folder_name( folder ), cache_name )


def __handle_missing_cache(mode, file_name):
    global __session_cache_skip
    
    if mode == ECache.ASK:
        if __session_cache_skip:
            return
        
        short_file_name = file_helper.get_last_directory_and_filename( file_name )
        
        Q_YES = "YES"
        Q_NO = "NO"
        Q_ALWAYS = "ALWAYS (for this session)"
        q_result = MCMD.question( "Cannot find the cache file «{0}» and the cache parameter is set to «{1}», which necessitates your response. Do you wish to continue?".format( short_file_name, mode ), Q_YES, Q_NO, Q_ALWAYS )
        
        if q_result is Q_YES:
            return
        elif q_result is Q_NO:
            raise FileNotFoundError( "Cannot find the cache file «{0}» and the user chose to abort the current operation.".format( file_name, mode ) )
        elif q_result is Q_ALWAYS:
            __session_cache_skip = True
            return
        else:
            raise SwitchError( "q_result", q_result )
    
    if mode == ECache.LOAD:
        raise FileNotFoundError( "Cannot find the cache file «{0}» and the cache parameter is set to «{1}», which prohibits the generation of new data.".format( file_name, mode ) )
    
    return


def __translate_cache_mode( mode: ECache ):
    if mode == ECache.DEFAULT:
        from neocommand.data.core import CORE
        mode = CORE.settings.default_cache_mode
        
        if mode == ECache.DEFAULT:
            mode = ECache.LOAD
    
    return mode


#endregion



