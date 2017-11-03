from typing import Optional, cast

import stringcoercion
from stringcoercion import Coercer, CoercionInfo

from intermake.visualisables.visualisable import IVisualisable
from intermake.visualisables.visualisable_operations import PathToVisualisable
from intermake.plugins import console_explorer


class VisualisableCoercion( Coercer ):
    def coerce( self, info: CoercionInfo ) -> Optional[ object ]:
        return console_explorer.re_select( path = info.source, dest_type = info.annotation.value, _sync = True )
    
    
    def can_handle( self, info: CoercionInfo ):
        return info.annotation.is_directly_below( PathToVisualisable ) or info.annotation.is_directly_below( IVisualisable )


class MAnnotationCoercer( Coercer ):
    def coerce( self, args: CoercionInfo ):
        return args.collection.coerce( args.annotation.mannotation_arg, args.source ) #the result is the type, not the annotation!
    
    
    def can_handle( self, info: CoercionInfo ):
        return info.annotation.is_mannotation
    
# Register them
stringcoercion.get_default_coercer().register( VisualisableCoercion(), MAnnotationCoercer() )
