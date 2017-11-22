from importlib import import_module
from types import ModuleType
from typing import List, Union

from os import path

from mhelper import file_helper


def load_namespace( module_: Union[ ModuleType, str ] ) -> None:
    """
    Registers a all plugins within a module or namespace.
    """
    if isinstance( module_, str ):
        module_ = import_module( module_ )
    
    for sub_module_name in list_namespace( module_ ):
        load_namespace( sub_module_name )


def list_namespace( module: ModuleType ) -> List[ str ]:
    """
    Given a module (i.e. a simple folder) finds the names of all sub-modules.
    
    :param module:    Module to search. 
    :return:          A list of module names, or if the module isn't a folder, an empty list. 
    """
    folder = get_module_path( module )
    
    if not path.isdir( folder ):
        return [ ]
    
    results = [ ]
    
    for file_name in file_helper.list_dir( folder, ".py" ) + file_helper.sub_dirs( folder ):
        module_name = file_helper.get_filename_without_extension( file_name )
        
        if not module_name.startswith( "_" ):
            module_name = module.__name__ + "." + module_name
            results.append( module_name )
    
    return results


def get_module_path( module: ModuleType ) -> str:
    """
    Gets the path to a module.
    """
    return module.__file__ if hasattr( module, "__file__" ) else module.__path__._path[ 0 ]
