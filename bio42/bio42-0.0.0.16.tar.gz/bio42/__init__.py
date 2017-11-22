def __setup() -> None:
    #
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ NeoCommand initialisation ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    #
    # noinspection PyUnresolvedReferences
    import neocommand
    from neocommand.helpers.database_helper import name_lookup
    from bio42 import constants
    
    name_lookup.update( { constants.NODE_SEQUENCE : "description",
                          constants.NODE_TAXON    : "scientific_name",
                          constants.NODE_GOCLASS  : "name",
                          constants.NODE_IPRCLASS : "name",
                          constants.NODE_PFAMCLASS: "name" } )
    #
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Intermake initialisation ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    #
    from mhelper import reflection_helper
    from intermake import MENV
    
    MENV.unlock( "neocommand" )
    MENV.name = "BIO42"
    MENV.abv_name = "B42"
    MENV.constants.update( (k, str( v )) for k, v in reflection_helper.public_dict( constants.__dict__ ).items() )
    MENV.version = "0.0.0.16"


__setup()

# Exports
from bio42.plugins.download_terms import download_terms
from bio42.plugins.parsers import parser_annotations, parser_blast, parser_csv, parser_go, parser_plugin, parser_sequence, parser_taxonomy
