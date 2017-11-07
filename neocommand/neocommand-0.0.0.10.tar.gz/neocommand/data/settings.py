from intermake import MENV
from mhelper import MEnum


__author__ = "Martin Rusilowicz"

class EResultsView( MEnum ):
    """
    How to view results
    
        `DEFAULT` - as the plugin dictates
        `LIST` - in the results viewer
        `BROWSER` - in the browser (only for Script plugins!)
    """
    DEFAULT = 0
    LIST = 1
    BROWSER = 2


class ENeo4jDriver( MEnum ):
    """
     Neo4j drivers
     
     :data NEO4JV1:    Neo4j official driver  
     :data PY2NEO:     Py2Neo third party driver 
    """
    NEO4JV1 = 1 #is a a bit better, though appears to have a memory leak.
    PY2NEO = 2 #gives more information out (notably it gives the nodes of a relationship, avoiding 0x000000 type IDs), but its quite buggy.
    

class Settings:
    """
    Main settings class

    USAGE:
        Settings.instance().xxx
    
    :data ssh_host                : SSH access
    :data ssh_user                : SSH credentials
    :data enable_browser          : Enable the GUI browser
    :data neo4j_binary_folder     : Binaries location
    :data is_unix                 : Path mode (for Neo4j, not us)
    :data default_cache_mode      : default cache mode
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        
        NOTE:
        The settings GUI is established via reflection, and therefore the settings *must* be strongly typed.
        Please use the `data` documentation to document the parameters.
        
        e.g. `self.my_setting = True` is acceptable (indicating a boolean "checkbox" setting), `self.my_setting = None` is not acceptable (the type cannot be determined).
        """
        from neocommand.helpers.cache_helper import ECache
                         
        self.ssh_host                               = ""
        self.ssh_user                               = ""
        self.enable_browser                         = False
        self.default_cache_mode                     = ECache.SELECT
    
    
    def save( self ):
        MENV.local_data.store[ "neocommand-settings" ] = self
    
