"""
Contains the `LocalData` class.
"""
import os
import warnings
from os import path
from typing import Callable, Iterator, Optional, Tuple, TypeVar, cast

from intermake.engine import constants
from mhelper import file_helper, io_helper, SimpleProxy, PropertySetInfo


__author__ = "Martin Rusilowicz"

T = TypeVar( "T" )

_AUTOSTORE_EXTENSION = ".pickle"


class _AutoStore:
    """
    Manages a local data store, loading and saving the keys to and from files in the specified folder.
    """
    
    
    def __init__( self, directory ):
        """
        CONSTRUCTOR
        :param directory:   Directory to use 
        """
        self.__directory = directory
        self.__data = { }
        self.__bound = { }
        file_helper.create_directory( directory )
        
        for file in os.listdir( directory ):
            if file.endswith( _AUTOSTORE_EXTENSION ):
                key = file_helper.get_filename_without_extension( file )
                self.__data[key] = self.__read_item( key )
    
    
    def bind( self, key: str, value: T ) -> T:
        """
        Binds to the specified setting object.
        If any changes have been made on disk, these will be propagated into `value`.
        `value` is wrapped in a proxy which detects changes, changes will then be automatically committed to disk.
        """
        existing = self.__data.get( key )
        
        if existing is None:
            self[key] = value
        else:
            updates = { }
            
            for pk, pv in value.__dict__.items():
                if pk.startswith( "_" ):
                    continue
                
                if pk in existing.__dict__:
                    epv = existing.__dict__[pk]
                    
                    updates[pk] = epv
            
            value.__dict__.update( updates )
        
        self.__bound[id( value )] = key
        
        return cast( T, SimpleProxy( source = value, watch = self.__proxy_changed ) )
    
    
    def __proxy_changed( self, e: PropertySetInfo ):
        key = self.__bound[id( e.source )]
        self.commit( key )
    
    
    def retrieve( self, key: str, type_: Callable[[], T] ) -> T:
        """
        Retrieves the setting from the cache
        :param key:     Setting key 
        :param type_:   Default (callable!), called if not present and saved 
        :return:        Setting 
        """
        result = self.__data.get( key )
        
        if result is None:
            result = type_()
            self[key] = result  # we must force a save, or the user won't see the settings in the editor plugins when we reload
        
        return result
    
    
    def commit( self, key: str ):
        """
        Saves the setting
        """
        self[key] = self.__data.get( key )
    
    
    def __getitem__( self, key ):
        """
        Returns the named setting
        """
        return self.__data[key]
    
    
    def __delitem__( self, key ):
        """
        Removes a setting
        """
        del self.__data[key]
        self.__write_item( key, None )
    
    
    def __setitem__( self, key, value ):
        """
        Sets the named setting and saves the file
        """
        self.__data[key] = value
        self.__write_item( key, value )
    
    
    def __read_item( self, key ):
        """
        Reads the specified setting from disk.
        """
        file_name = path.join( self.__directory, key + _AUTOSTORE_EXTENSION )
        
        if not path.isfile( file_name ):
            return None
        
        try:
            result = io_helper.load_binary( file_name )
        except Exception as ex:
            # Data cannot be restored - ignore it
            warnings.warn( "Failed to restore settings from «{0}» due to the error «{1}».".format( file_name, ex ), UserWarning )
            return None
        
        if type( result ) is dict:
            return result
        
        return io_helper.default_values( result )
    
    
    def __write_item( self, key, value ):
        """
        Saves the settings to disk
        """
        file_name = path.join( self.__directory, key + _AUTOSTORE_EXTENSION )
        
        if value is not None:
            io_helper.save_binary( file_name, value )
        else:
            os.remove( file_name )
    
    
    def __contains__( self, key ):
        """
        Returns if the specified setting exists.
        """
        return key in self.__data
    
    
    def keys( self ):
        """
        Returns saved settings
        """
        return self.__data.keys()
    
    
    def get( self, settings_key, default_value ):
        result = self.__data.get( settings_key, None )
        
        if result is None:
            result = default_value
        
        return result
    
    
    def get_and_init( self, settings_key: str, default_value: T ) -> T:
        """
        Gets the setting
        If properties are missing from the result, initialises them with "default"
        """
        result = self.__data.get( settings_key )
        
        if result is None:
            self[settings_key] = default_value
            return default_value
        
        dirty = False
        
        for dict_key, value in default_value.__dict__.items():
            if dict_key not in result.__dict__ \
                    or type( result.__dict__[dict_key] ) != type( value ):
                result.__dict__[dict_key] = value
                warnings.warn( "LocalData.get_and_init - Adding {0} {1} = {2} to {3} because it wasn't already there.".format( type( value ).__name__, dict_key, value, settings_key ), UserWarning )
                dirty = True
        
        if dirty:
            self.__write_item( settings_key, result )
        
        return result
    
    
    def __len__( self ):
        """
        Number of settings stored
        """
        return len( self.__data )
    
    
    def starting( self, prefix: str ) -> Iterator[Tuple[str, Optional[object]]]:
        """
        Gets all our local data with keys starting with a specified prefix.
        :param prefix: The prefix to search 
        :return: Tuple of key, value. 
        """
        for key, value in self.__data.items():
            if key.startswith( prefix ):
                yield key[len( prefix ):], value


class LocalData:
    """
    Manages $(APPNAME)'s primary working directory, usually "~/$(ABVNAME)-data" (UNIX) or "%user%/$(ABVNAME)-data" (Windows).
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.__workspace: Optional[str] = None
        self.__workspace_in_use: bool = False
        self.__store: _AutoStore = None
    
    
    def get_workspace( self ) -> str:
        """
        Obtains the workspace folder.
        Once this is called, `set_workspace` no longer functions.
        """
        if self.__workspace is None:
            self.set_workspace( None )
        
        self.__workspace_in_use = True
        
        assert isinstance( self.__workspace, str )
        return self.__workspace
    
    
    def set_workspace( self, value: Optional[str] ) -> None:
        """
        Overrides the default workspace folder.
        This can only be done before settings, etc. are loaded and saved.
        To set the workspace permanently, `set_redirect` should be called instead.
        
        Nb. If this is set to `None` the default workspace or redirection is used.
        
        :param value:   New workspace. You can use "~" for the user's home directory. 
        """
        if self.__workspace_in_use:
            raise ValueError( "Cannot change the workspace to «{}» because the existing workspace «{}» is already in use.".format( value, self.__workspace ) )
        
        # Working folder
        if value is None:
            value = self.get_redirect() or self.default_workspace()
        else:
            value = value
        
        if not value or path.sep not in value:
            raise ValueError( "A complete workspace path is required, «{}» is not valid.".format( self.__workspace ) )
        
        if "~" in value:
            value = path.expanduser( value )
        
        self.__workspace = value
    
    
    def set_redirect( self, content: Optional[str] ) -> None:
        """
        Sets or clears the workspace redirection.
        """
        r = self.__get_redirect_file_name()
        
        if content:
            file_helper.write_all_text( r, content )
        else:
            file_helper.delete_file( r )
    
    
    def get_redirect( self ) -> Optional[str]:
        """
        Gets the current redirection.
        """
        redirect = self.__get_redirect_file_name()
        
        if path.isfile( redirect ):
            return file_helper.read_all_text( redirect ).strip()
        else:
            return None
    
    
    @classmethod
    def default_workspace( cls ) -> str:
        from intermake.engine.environment import MENV
        
        abv = MENV.abv_name
        
        if abv == constants.DEFAULT_NAME:
            raise ValueError( "Attempt to the obtain default workspace without setting the application name." )
        
        return path.join( "~", ".intermake-data", abv.lower() )
    
    
    @property
    def store( self ) -> _AutoStore:
        """
        Obtains the settings store.
        """
        if self.__store is None:
            self.__store = _AutoStore( self.local_folder( constants.FOLDER_SETTINGS ) )
        
        # noinspection PyTypeChecker
        return self.__store
    
    
    @classmethod
    def __get_redirect_file_name( cls ) -> str:
        """
        Obtains the name of the file used to redirect the default workspace.
        """
        return cls.default_workspace() + ".dir"
    
    
    def local_folder( self, name: str ) -> str:
        """
        Obtains a folder in the workspace. See `intermake.engine.constants.FOLDER_*` for suggested defaults.
        """
        folder_name = path.join( self.get_workspace(), name )
        file_helper.create_directory( folder_name )
        return folder_name
