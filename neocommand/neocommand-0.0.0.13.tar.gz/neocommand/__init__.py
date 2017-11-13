def __setup():
    #
    # INTERMAKE Setup
    #
    from mhelper import reflection_helper
    from intermake import MENV
    from neocommand.extensions import plugins
    from neocommand.data import constants
    from neocommand.data.core import CORE
    
    MENV.name = "NeoCommand"
    MENV.constants.update( (k, str( v )) for k, v in reflection_helper.public_dict( constants.__dict__ ).items() )
    MENV.root = CORE
    MENV.plugins.legacy_load_namespace( plugins )
    
    #
    # EDITORIUM Setup
    #
    import editorium
    
    
    def __register():
        from neocommand.extensions.hosts.gui_editorium_extensions import Editor_SpecialString
        return Editor_SpecialString
    
    
    editorium.register( __register )


# Setup MCMD *before* exporting CORE
__setup()

# Export stuff
from neocommand.data import constants
from neocommand.data.core import CORE
from neocommand.data.settings import Settings, ENeo4jDriver
from neocommand.database.endpoints import IEndpoint, CountingEndpointWrapper
from neocommand.helpers.neo_csv_helper import NEO_TYPE_COLLECTION
from neocommand.extensions.plugins.basic import database, endpoints
from neocommand.extensions.plugins.exportation import exportation, neo_csv_exports, neo_csv_exchange, neo_csv_tools 

