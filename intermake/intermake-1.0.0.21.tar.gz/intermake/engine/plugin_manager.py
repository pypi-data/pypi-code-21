import inspect
from importlib import import_module
from types import ModuleType
from typing import List, cast, Any, Dict, Iterator, Optional, Union, Tuple
from warnings import warn

from intermake.engine import constants
from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo
from mhelper import file_helper, string_helper, module_helper
from mhelper.exception_helper import SwitchError


__author__ = "Martin Rusilowicz"

TModule = Union[ModuleType, str]
TPlugin = "intermake.engine.plugin.Plugin"
TPluginFolder = "intermake.engine.plugin_manager.PluginFolder"
TPluginOrModuleOrList = Union[ModuleType, TPluginFolder, TPlugin, List[Union[ModuleType, TPluginFolder, TPlugin] ], Tuple[Union[ModuleType, TPluginFolder, TPlugin] ] ]


class PluginManager:
    """
    Manages the set of user-defined functions formally identified as "plugins"
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self._plugins_root = PluginFolder( constants.EXPLORER_KEY_PLUGINS, "All loaded Plugins", None )
        self.__all_plugins = []
        
    def to_callable(self) -> Any:
        """
        Returns an object the caller can call the plugins on.
        """
        result = object()
        result.__dict__ = self.to_dictionary()
        return result
    
    
    def to_dictionary( self ) -> Dict[str, TPlugin]:
        """
        Returns a dictionary of the plugins.
        :return: 
        """
        from intermake.engine.plugin import Plugin
        
        r: Dict[str, Plugin] = { }
        
        # Names to avoid overriding, we don't want to override `exit` but we do want to
        # override `help`.
        avoid = ["exit"]
        
        for x in self.all_plugins():  # type: Plugin
            if x.is_visible:
                for n in x.names:
                    if n not in avoid:
                        r[n] = x
        
        return r
    
    
    def remove( self, value : TPluginOrModuleOrList ):
        """
        Removes one or more plugins.
        
        :param value:   Plugins to remove.
                        * A single plugin
                        * A list of plugins
                        * A module
                        * One of the special values:
                            * "explorer"
                            * "defaults"
                            * "common"
        :return: 
        """
        from intermake.engine.plugin import Plugin
        
        if isinstance( value, ModuleType ):
            self.remove( self.__register_module( value ) )
        elif isinstance( value, PluginFolder ):
            value.parent.remove_child( value )
        elif isinstance( value, Plugin ):
            value.parent.remove_child( value )
        elif isinstance( value, list ) or isinstance( value, tuple ):
            for value_ in value:
                self.remove( value_ )
        else:
            raise SwitchError( "value", value, instance = True )
    
    
    def register( self, plugin: TPlugin, module_ : Optional[TModule] = None ):
        """
        Registers a plugin.
        :param module_:  Module to register under. If `None` uses the calling module. 
        :param plugin:   Plugin to register.
        """
        if module_ is None:
            frame = inspect.stack()[1]
            module_ = inspect.getmodule( frame[0] )
        
        from intermake.engine.plugin import Plugin
        
        assert isinstance( plugin, Plugin )
        
        # Check that it isn't already registered
        if plugin in self.__all_plugins or plugin.parent:
            raise KeyError(
                    "The plugin «{0}» is exported by both \"{1}\" and \"{2}\". Check that you haven't accidentally re-exported a plugin imported from another module. Did you use accidentally `import x.y` instead of `import x`?".format(
                            plugin.name, plugin.parent, module_ ) )
        
        # Add the plugin itself
        if plugin.folder:
            folder = self.__register_folder( "", plugin.folder )
        else:
            folder = self.__register_module( module_ )
        
        plugin.parent = folder
        folder.add_child( plugin )
        self.__all_plugins.append( plugin )
        
        # Fix the names
        for ex_plugin in self.all_plugins():
            if ex_plugin is not plugin:
                conflicts = []
                
                for name_1 in plugin.names:
                    if name_1 in ex_plugin.names:
                        conflicts.append( name_1 )
                
                for conflict in list( conflicts ):
                    ex_plugin.names.remove( conflict )
                    
                    if len( ex_plugin.names ) == 0:
                        ex_plugin.names.append( "cmd_{}".format( id( ex_plugin ) ) )
                    else:
                        conflicts.remove( conflict )
                
                if conflicts:
                    warn( "A plugin with a name in {} is exported \"{}\", after it had been created by \"{}\", the original has been renamed to \"{}\". This looks like the plugins just have the same name, but check that you haven't accidentally re-exported a plugin imported from another module. Did you use accidentally `import x.y` instead of `import x`?".format(
                            conflicts,
                            plugin.parent,
                            ex_plugin.parent,
                            ex_plugin.name ), UserWarning )
    
    
    @staticmethod
    def legacy_load_namespace( namespace : TModule ):
        """
        Utility function that loads all modules in a namespace.
        This replaces old _register-all-in-namespace_ type functions that are now replaced by plugin self-registration.
        """
        module_helper.load_namespace( namespace )
    
    
    def __register_module( self, module_: TModule ):
        """
        Retrieves the `PluginFolder` object representing the specified module.
        """
        name, docs = self.__module_name_and_docs( module_ )
        
        return self.__register_folder( docs, name )
    
    
    def __register_folder( self, docs : str, name : str ):
        for folder in self._plugins_root.contents:  # type: PluginFolder
            if folder.name == name:
                if docs:
                    if docs not in folder.description:
                        folder.description += "\n\n" + docs
                
                return folder
        
        folder = PluginFolder( name, docs, self._plugins_root )
        self._plugins_root.contents.append( folder )
        return folder
    
    
    @staticmethod
    def __module_name_and_docs( module_: TModule ):
        if isinstance( module_, str ):
            module_ = import_module( module_ )
        
        doc = module_.__doc__ or ""
        
        if doc:
            doc = doc.strip() + "\n\n"
        
        path = module_helper.get_module_path( module_ )
        
        doc += "This module contains the set of plugins from `" + path + "`:"
        
        name = file_helper.get_filename_without_extension( path )
        name = string_helper.undo_camel_case( name, "_" )
        
        for attr in ["mcmd_folder_name", "_mcmd_folder_name_", "__mcmd_folder_name__"]:
            name = getattr( module_, attr, name )
        
        return name, doc
    
    
    def __iter__( self ) -> "Iterator[.engine.plugin.Plugin]":
        """
        OVERRIDE 
        """
        return iter( self.all_plugins() )
    
    
    def plugins( self ) -> "PluginFolder":
        return self._plugins_root
    
    
    @classmethod
    def __iterate( cls, x ):
        from intermake.engine.plugin import Plugin
        
        if isinstance( x, Plugin ):
            yield x
            
            for c in x.children():
                yield from cls.__iterate( c )
        
        elif isinstance( x, PluginFolder ):
            for c in x.contents:
                yield from cls.__iterate( c )
        else:
            raise SwitchError( "x", x )
    
    
    def all_plugins( self ) -> "List[.engine.plugin.Plugin]":
        from intermake.engine.plugin import Plugin
        return cast( List[Plugin], self.__all_plugins )


class PluginFolder( IVisualisable ):
    """
    A collection of plugins organised into a folder.
    """
    
    def __init__( self, name: str, doc: str, parent: "Optional[PluginFolder]" ) -> None:
        """
        Constructor
        :param name:    Folder name 
        :param doc:     Documentation 
        :param parent:  Parent folder (if any) 
        """
        self.name = name
        self.contents = []
        self.description = doc
        self.parent = parent
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        num_plugins = len( self )
        num_modules = sum( isinstance( x, PluginFolder ) for x in self.contents )
        
        if num_modules:
            if num_plugins != num_modules:
                text = "{0} plugins".format( num_plugins )
            else:
                text = "{0} modules".format( num_modules )
        else:
            if num_plugins:
                text = "{0} plugins".format( num_plugins )
            else:
                text = "No plugins".format( num_plugins )
        
        return UiInfo( name = self.name,
                       comment = self.description,
                       type_name = constants.VIRTUAL_FOLDER,
                       value = text,
                       colour = EColour.YELLOW,
                       icon = resources.folder,
                       extra_named = self.contents )
    
    
    def __len__( self ) -> int:
        """
        OVERRIDE 
        """
        return len( self.contents )
    
    
    def __iter__( self ) -> "Iterator[.intermake.engine.plugin.Plugin]":
        """
        OVERRIDE 
        """
        from intermake.engine.plugin import Plugin
        yield from (x for x in self.contents if isinstance( x, Plugin ))
    
    
    def __str__( self ):
        """
        OVERRIDE 
        """
        return self.name
    
    
    def add_child( self, child_plugin ):
        """
        :type child_plugin: Union[Plugin, PluginFolder]
        """
        self.contents.append( child_plugin )
    
    
    def remove_child( self, child_plugin ):
        """
        :type child_plugin: Union[Plugin, PluginFolder]
        """
        self.contents.remove( child_plugin )
