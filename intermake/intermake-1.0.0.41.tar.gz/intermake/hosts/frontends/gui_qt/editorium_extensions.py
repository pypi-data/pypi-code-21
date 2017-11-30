from typing import Optional

from mhelper import exception_helper

from editorium.editorium_qt import Editor_TextBrowsableBase, EditorInfo
from intermake.engine.environment import MENV
from intermake.visualisables.visualisable import IVisualisable
from intermake.visualisables.visualisable_operations import PathToVisualisable
from intermake.plugins import console_explorer


class Editor_Visualisable( Editor_TextBrowsableBase ):
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
        return info.inspector.is_directly_below_or_optional( IVisualisable ) \
               or info.inspector.is_directly_below_or_optional( PathToVisualisable )
    
    
    def on_browse( self, value: IVisualisable ) -> Optional[PathToVisualisable]:
        underlying_type = self.info.inspector.type_or_optional_type
        
        if issubclass( underlying_type, PathToVisualisable ):
            underlying_type = underlying_type.type_restriction() or IVisualisable
        
        from intermake.hosts.frontends.gui_qt.frm_tree_view import FrmTreeView
        
        return FrmTreeView.request( self.editor.window(),
                                    "Select " + self.info.inspector.name,
                                    None,
                                    lambda x: isinstance( x.get_value(), underlying_type ) )
    
    
    def on_get_default_value( self ) -> str:
        return self.on_convert_to_text( PathToVisualisable.find_path( MENV.root ) )
    
    
    def on_convert_to_text( self, value ):
        return str( value )
    
    
    def on_convert_from_text( self, text ):
        return console_explorer.re_select( path = text, dest_type = PathToVisualisable, _sync = True )
    
    
    def set_value( self, value: Optional[object] ):
        super().set_value( value )
    
    
    def get_value( self ):
        value = super().get_value()
        exception_helper.assert_type( "value", value, PathToVisualisable )
        concrete_type = self.info.inspector.type_or_optional_type
        
        if issubclass( concrete_type, PathToVisualisable ):
            assert isinstance( value, PathToVisualisable ), value
            return value
        else:
            return value.get_last()
