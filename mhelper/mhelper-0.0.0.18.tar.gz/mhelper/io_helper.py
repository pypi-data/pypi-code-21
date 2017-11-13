"""
Load and save functions
"""
import warnings
from typing import Optional, TypeVar, Union, cast


T = TypeVar("T")


CAUSE_ERROR = object # Sentinel object for load_* functions

def load_npy( file_name ):
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    
    if file_name.upper().endswith( ".NPZ" ):
        result = result[ "data" ]
    
    return result


def load_npz( file_name ):
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    result = result[ "data" ]
    
    return result

def save_bitarray(file_name : str, value) -> None:
    """
    Saves a bit array
    
    :type value: bitarray
    
    :param file_name: File name
    :param value: Value to save
    """
    from bitarray import bitarray
    from mhelper.exception_helper import SubprocessError
    from mhelper import exception_helper, file_helper
    
    exception_helper.assert_instance( "save_bitarray::value", value, bitarray )
    assert isinstance(value, bitarray) 
    
    try:
        with open(file_name, "wb") as file_out:
            value.tofile(file_out)
    except TypeError:
        # Stupid "open file expected" error on OSX (due to bug writing large files - fallback to manual implementation)
        _save_bytes_manually( file_name, value.tobytes() )
    except Exception as ex:
        raise SubprocessError("Failed to write bitarray of length {} to «{}».".format(len(value), file_name)) from ex
    
    size = float( file_helper.file_size( file_name ) )
    expected = len(value)
    
    if size < expected / 8.0:
        raise ValueError("Saved file is shorter ({} bytes or {} bits) than the originating bitarray ({} bytes or {} bits).".format(size, size * 8, expected / 8, expected))
    
def _save_bytes_manually( file_name: str, value: bytes ):
    """
    Fallback function used by `save_bitarray`.
    """
    warnings.warn( "Save bitarray failed. This is probably due to an error in your `bitarray` library. The file will be saved incrementally but this will take longer.", UserWarning )
    BATCH_SIZE = 100000
    cursor = 0
    length = len( value )
    
    with open( file_name, "wb" ) as file_out: #note that writing large arrays on OSX is probably the problem, we can't just dump the bytes
        while cursor < length:
            next = min( cursor + BATCH_SIZE, length )
            slice = value[ cursor:next ]
            file_out.write( slice ) 
            cursor = next
            
def _read_bytes_manually(file_name:str)->bytes:
    BATCH_SIZE = 100000
    b = bytearray()
    
    with open( file_name, "rb" ) as file_in:
        while True:
            buf = file_in.read( BATCH_SIZE )
            
            if len( buf ) == 0:
                break
            
            b.extend( buf )
    
    return bytes( b )

def load_bitarray(file_name : str):
    """
    Loads a bitarray
    :param file_name: File to read 
    :return: bitarray. Note this may be padded with missing bits. 
    """
    from bitarray import bitarray
    
    result = bitarray()
    
    try:
        with open(file_name, 'rb') as file_in:
            result.fromfile(file_in)
    except SystemError: #OSX error
        result = bitarray()
        result.frombytes(_read_bytes_manually(file_name))
        assert len(result)!=0
        
    return result


def save_npy( file_name, value ):
    import numpy
    
    numpy.save( file_name, value, allow_pickle = False, fix_imports = False )


def save_npz( file_name, value ):
    import numpy
    
    numpy.savez_compressed( file_name, data = value )


def load_binary( file_name : str, default : Optional[object] = CAUSE_ERROR ):
    """
    Loads a binary file
    
    :param file_name: Filename to load  
    :param default:     Whether to default the values (if not specified or `cause_error` an exception is raised) 
    :return: Loaded file, or `default` (if specified) 
    """
    try:
        import pickle
        
        with open( file_name, "rb" ) as file:
            return pickle.load( file, fix_imports = False )
    except:
        if default is CAUSE_ERROR:
            raise
        
        return default


def save_binary( file_name, value ):
    import pickle
    
    with open( file_name, "wb" ) as file:
        pickle.dump( value, file, fix_imports = False )


def load_json( file_name, keys = True ):
    from mhelper.file_helper import read_all_text
    import jsonpickle
    
    text = read_all_text( file_name )
    
    return jsonpickle.decode( text, keys = keys )


def save_json( file_name, value, keys = True ):
    from mhelper.file_helper import write_all_text
    import jsonpickle
    
    write_all_text( file_name, jsonpickle.encode( value, keys = keys ) )


def default_values( target: T, default: Optional[ Union[ T, type ] ] = None ) -> T:
    if default is None:
        if target is None:
            raise ValueError("Cannot set the defaults for the value because both the value and the defaults are `None`, so neither can be inferred.")
        
        default = type(target)
        
    if isinstance(default, type):
        default = default()
    
    if target is None:
        return default
    
    if isinstance(target, list):
        return cast(T, target)
    
    # TODO: PUT THIS BACK IN! Removed because for some reason we get a different class when deserialising from the IDE, but this is a problem!
    # if type(target) is not type(default):
    #     raise ValueError("Attempting to set the defaults for the value «{}», of type «{}», but the value provided, «{}», of type «{}», is not compatible with this.".format(target, type(target), default, type(default)))
    
    for k, v in default.__dict__.items():
        if k.startswith("_"):
            continue
            
        if k not in target.__dict__:
            target.__dict__[k] = v

    to_delete = []
            
    for k in target.__dict__.keys():
        if k not in default.__dict__:
            to_delete.append(k)

    for k in to_delete:
        del target.__dict__[k]
            
    return target