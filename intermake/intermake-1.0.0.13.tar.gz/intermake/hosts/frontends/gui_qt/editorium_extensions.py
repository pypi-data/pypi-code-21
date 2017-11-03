from typing import Optional

from editorium.editorium_qt import Editor_BrowsableBase, EditorInfo
from intermake.visualisables.visualisable import IVisualisable
from intermake.visualisables.visualisable_operations import PathToVisualisable
from intermake.plugins import console_explorer


class Editor_Visualisable(Editor_BrowsableBase):
    """
    Edits:  IVisualisable 
            IOrigin 
            IEndpoint 
            Optional[IVisualisable]
            Optional[IOrigin]
            Optional[IEndpoint]
    """
    def __init__( self, info: EditorInfo ):        
        super().__init__( info, False )
        
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_type_or_optional_type_subclass( IVisualisable ) \
               or info.inspector.is_type_or_optional_type_subclass( PathToVisualisable )


    def browse_for_value( self, text ) -> Optional[ object ]:
        
        
        underlying_type = self.info.inspector.type_or_optional_type
        
        if issubclass(underlying_type, PathToVisualisable):
            # noinspection PyUnresolvedReferences
            underlying_type = underlying_type.type_restriction() or IVisualisable
        
        from intermake.hosts.frontends.gui_qt.frm_tree_view import FrmTreeView
        return FrmTreeView.request( None, "Select " + self.info.inspector.name, None, lambda x: isinstance( x, underlying_type ) )
    
    def convert_to_text(self, value):
        return str(value)
    
    def convert_from_text(self, text):
        
        try:
            return console_explorer.re_select( path = text, dest_type = self.info.inspector.type_or_optional_type, _sync = True )
        except:
            return None


    def set_value( self, value: Optional[ object ] ):
        super().set_value(value)
        
    def get_value( self ):
        value = super().get_value()
        
        concrete_type = self.info.inspector.type_or_optional_type
        
        if issubclass(concrete_type, PathToVisualisable):
            assert isinstance(value, PathToVisualisable)
            return value
        elif isinstance(value, PathToVisualisable):
            return value.get_last()
        else:
            return value
        

