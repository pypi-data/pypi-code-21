"""
Provides the GUI editors for node and edge, labels and properties.

These editors are registered with the EDITORIUM package in `hosts.gui`
"""

from editorium.editorium_qt import EditorBase, EditorInfo

from neocommand import CORE
from neocommand.helpers.special_types import TEdgeLabel, TNodeLabel, TEntityProperty


class Editor_SpecialString( EditorBase ):
    """
    Edits:  TEdgeLabel 
            TNodeLabel
            TEntityProperty
            Optional[TEdgeLabel]
            Optional[TNodeLabel]
            Optional[TEntityProperty]
    """
    
    
    def __init__( self, info: EditorInfo ):
        from PyQt5.QtWidgets import QComboBox
        self.editor = QComboBox(  )
        self.editor.setEditable( True )
        from editorium.constants import OPTION_ENUM_NONE
        self.option_none = info.messages.get( str( OPTION_ENUM_NONE ), "None" )
        
        if info.inspector.is_optional:
            self.editor.addItem( self.option_none )
        
        if info.inspector.type_or_optional_type is TEdgeLabel:
            for x in CORE.name_cache.edge_labels():
                self.editor.addItem( x.name )
        
        if info.inspector.type_or_optional_type is TNodeLabel:
            for x in CORE.name_cache.node_labels():
                self.editor.addItem( x.name )
        
        if info.inspector.type_or_optional_type is TEntityProperty:
            # noinspection PyUnresolvedReferences
            for x in CORE.name_cache.properties( info.type.type_label() ):
                self.editor.addItem( x.name )
        
        super().__init__( info, self.editor )
        
        self.editor.currentTextChanged[ str ].connect( self.__currentTextChanged )
        self.editor.setCurrentText( self.option_none )
    
    
    def __currentTextChanged( self, _: str ):
        self.info.editorium.set_none_state( self.editor, self.get_value(), self.info.inspector.is_optional )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.type_or_optional_type in (TEdgeLabel, TNodeLabel, TEntityProperty)
    
    
    def set_value( self, value ):
        if value is None:
            self.editor.setCurrentText( self.option_none )
        else:
            self.editor.setCurrentText( value )
    
    
    def get_value( self ):
        text = self.editor.currentText()
        
        if text == self.option_none or not text:
            return None
        
        return text
