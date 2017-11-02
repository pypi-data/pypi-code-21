import sip
from enum import Enum
from typing import Dict, Optional, cast

from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QCheckBox, QComboBox, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QSpacerItem, QSpinBox, QToolButton, QWidget, QRadioButton
from flags import Flags

from mhelper import SwitchError, abstract, exceptToGui, override, EFileMode, Filename, HReadonly, AnnotationInspector, FileNameAnnotation

from editorium import constants


def __combine( x: Dict[Flags, QCheckBox] ):
    t = next( iter( x.keys() ) )
    # noinspection PyUnresolvedReferences
    value = t.__no_flags__
    
    for k, v in x:
        if v.isChecked():
            value |= k
    
    return value


class EditorInfo:
    def __init__( self, editorium: "Editorium", type_, messages: Dict[object, object] ):
        self.editorium = editorium
        self.inspector = AnnotationInspector( type_ )
        self.messages = messages


class EditorBase:
    """
    Base editor class
    """
    
    
    def __init__( self, info: EditorInfo, editor: QWidget ):
        """
        CONSTRUCTOR
        :param info:        `info` passed to derived class constructor 
        :param editor:      Editor widget created by derived class 
        """
        self.info = info
        self.editor = editor
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        """
        Determines if this type can handle editing this type.
        """
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> Optional[object]:
        """
        Obtains the value stored in the editor.
        It is the caller's responsibility to verify the result; the return value does not need to
        commute with the intended type (self.info). e.g. if the user has not chosen a file from a
        file browser, `None` may be returned.
        """
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: Optional[object] ):
        """
        Sets the value of the editor.
        :param value:   A value that commutes with `self.info`
        """
        raise NotImplementedError( "abstract" )
    
    
    def handle_changes( self, signal ):
        """
        The derived class should to register signal handling.
        """
        signal.connect( self.__change_occurred )
    
    
    # noinspection PyUnusedLocal
    @exceptToGui()
    def __change_occurred( self, *args, **kwargs ):
        """
        Handles changes to the editor.
        """
        pass


class Editorium:
    """
    Holds the set of editors.
    
    :data editors:              Array of editor types.
    :data default_messages:     Always appended to `messages`. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.editors = []
        self.default_messages = { }
    
    
    def register( self, editor: EditorBase ):
        """
        Registers an editor with this Editorium.
        """
        self.editors.insert( len( self.editors ) - 1, editor )
    
    
    def get_editor( self, type_: type, *, messages: Optional[Dict[object, object]] = None ) -> EditorBase:
        """
        Constructs a suitable editor for this type.
        :param messages:    Optional array of messages to pass to the editors. e.g. the OPTION_* fields in `editorium.constants`. See also `Editorium().default_messages` 
        :param type_:       Type of value to create editor for. Basic types, as well as most of `typing` and `mhelper.special_types` should be handled.
        :return: 
        """
        messages_d = dict( self.default_messages )
        
        if messages is not None:
            messages_d.update( messages )
        
        info = EditorInfo( self, type_, messages_d )
        
        for x in self.editors:
            if x.can_handle( info ):
                r = x( info )
                assert hasattr( r, "editor" ) and r.editor is not None, "«{}» didn't call the base class constructor.".format( x )
                return r
        
        raise ValueError( "No suitable editor found for «{}». This is an internal error and suggests that a working fallback editor has not been provided. The list of editors follows: {}".format( type_, self.editors ) )


class Editor_Nullable( EditorBase ):
    """
    Edits: Optional[T] (as a fallback for editors of `T` not supporting `None` as an option)
    """
    
    
    def __init__( self, info: EditorInfo ):
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        self.editor = QFrame()
        self.editor.setLayout( layout )
        
        self.checkbox = QCheckBox()
        # noinspection PyUnresolvedReferences
        self.checkbox.stateChanged[int].connect( self.__on_checkbox_toggled )
        self.checkbox.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        
        self.option_visual_tristate = info.messages.get( constants.OPTION_VISUAL_TRISTATE, False )
        self.option_hide = info.messages.get( constants.OPTION_HIDE, False )
        self.checkbox.setText( self.option_hide if not isinstance( self.option_hide, bool ) else "" )
        self.option_align_left = self.option_hide and info.messages.get( constants.OPTION_ALIGN_LEFT, False )
        
        if self.option_visual_tristate:
            self.checkbox.setTristate( True )
        
        layout.addWidget( self.checkbox )
        
        underlying_type = info.inspector.optional_type
        
        self.sub_editor = info.editorium.get_editor( underlying_type, messages = info.messages )
        self.sub_editor.editor.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        layout.addWidget( self.sub_editor.editor )
        
        if self.option_align_left:
            self.non_editor = QLabel()
            self.non_editor.setText( "" )
            self.non_editor.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
            layout.addWidget( self.non_editor )
        
        self.__on_checkbox_toggled( self.checkbox.isChecked() )
        
        super().__init__( info, self.editor )
    
    
    @exceptToGui()
    def __on_checkbox_toggled( self, _: int ):
        if self.option_visual_tristate:
            if self.checkbox.checkState() == Qt.Unchecked:
                self.checkbox.setCheckState( Qt.PartiallyChecked )
                return
        
        state = self.checkbox.checkState() == Qt.Checked
        
        if self.option_hide:
            self.sub_editor.editor.setVisible( state )
        else:
            self.sub_editor.editor.setEnabled( state )
        
        if self.option_align_left:
            self.non_editor.setVisible( not state )
        
        if state:
            self.checkbox.setText( "" )
        elif self.option_hide:
            self.checkbox.setText( str( self.option_hide ) if self.option_hide is not True else "" )
    
    
    def get_value( self ) -> Optional[object]:
        if self.checkbox.isChecked():
            return self.sub_editor.get_value()
        else:
            return None
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_optional
    
    
    def set_value( self, value: Optional[object] ) -> None:
        self.checkbox.setChecked( value is not None )
        self.__on_checkbox_toggled( self.checkbox.isChecked() )


class Editor_String( EditorBase ):
    """
    Edits: str
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        
        super().handle_changes( self.editor.textChanged[str] )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_direct_sub_class( str )
    
    
    def set_value( self, value: str ):
        self.editor.setText( str( value ) )
    
    
    def get_value( self ) -> str:
        return self.editor.text()


class Editor_Annotation( EditorBase ):
    def __init__( self, info: EditorInfo ):
        self.delegate = info.editorium.get_editor( info.inspector.mannotation_arg, messages = info.messages )
        
        super().__init__( info, self.delegate.editor )
    
    
    def set_value( self, value: Optional[object] ):
        self.delegate.set_value( value )
    
    
    def get_value( self ) -> Optional[object]:
        return self.delegate.get_value()
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_mannotation


class Editor_List( EditorBase ):
    """
    Edits: List[T]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.list_type = info.inspector.list_type
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        self.spinner = QSpinBox()
        self.spinner.setValue( 1 )
        self.spinner.valueChanged.connect( self.__valueChanged )
        self.spinner.setButtonSymbols( QAbstractSpinBox.UpDownArrows )
        self.layout.addWidget( self.spinner )
        
        self.editor = QFrame()
        self.editor.setLayout( self.layout )
        
        self.editors = []
        
        super().__init__( info, self.editor )
        
        self.__add_editor()
    
    
    @exceptToGui()
    def __valueChanged( self, num_editors: int ):
        while len( self.editors ) > num_editors:
            self.__remove_editor()
        
        while len( self.editors ) < num_editors:
            self.__add_editor()
    
    
    def __add_editor( self ):
        editor = self.info.editorium.get_editor( self.list_type )
        self.layout.addWidget( editor.editor )
        self.editors.append( editor )
    
    
    def __remove_editor( self ):
        editor = self.editors.pop()
        self.layout.removeWidget( editor.editor )
        sip.delete( editor.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_list
    
    
    def set_value( self, value ):
        self.spinner.setValue( len( value ) )
        
        for i, x in enumerate( value ):
            self.editors[i].set_value( x )
    
    
    def get_value( self ):
        r = []
        
        for x in self.editors:
            v = x.get_value()
            r.append( v )
        
        return r


class Editor_Fallback( EditorBase ):
    """
    Last resort editor for concrete objects that just returns strings.
    
    Edits: object
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QLineEdit()
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.value is not type( None )
    
    
    def set_value( self, value: object ) -> None:
        if value is None:
            raise TypeError( "Editor_Fallback set_value to None but this doesn't commute with the type «{}».".format( self.info.inspector.value ) )
        
        self.editor.setText( str( value ) )
    
    
    def get_value( self ):
        return self.editor.text()


class Editor_Enum( EditorBase ):
    """
    Edits:  Enum
            Optional[Enum]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QComboBox()
        # noinspection PyTypeChecker
        
        self.items = list( info.inspector.type_or_optional_type )
        self.option_none = info.messages.get( str( constants.OPTION_ENUM_NONE ), "None" )
        
        self.editor.setEditable( False )
        
        if info.inspector.is_optional:
            self.editor.addItem( self.option_none )
        
        self.editor.addItems( x.name for x in self.items )
        
        super().handle_changes( self.editor.currentIndexChanged[int] )
        
        super().__init__( info, self.editor )
        
        self.set_value( None )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_type_or_optional_type_subclass( Enum )
    
    
    def set_value( self, value: object ):
        if self.info.inspector.is_optional:
            if value is None:
                self.editor.setCurrentIndex( 0 )
                return
        
        self.editor.setCurrentIndex( self.items.index( value ) + self.__offset() )
    
    
    def __offset( self ):
        return 1 if self.info.inspector.is_optional else 0
    
    
    def get_value( self ):
        if self.info.inspector.is_optional:
            if self.editor.currentIndex() == 0:
                return None
        
        return self.items[self.editor.currentIndex() - self.__offset()]


@abstract
class Editor_BrowsableBase( EditorBase ):
    """
    ABSTRACT
    """
    
    
    @classmethod
    @abstract
    @override
    def can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def __init__( self, info: EditorInfo, textual: bool ):
        self.textual = textual
        self.validated_value = None
        
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        
        editor = QFrame()
        editor.setLayout( layout )
        
        self.line_edit = QLineEdit()
        self.line_edit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.line_edit.setPlaceholderText( "" )
        
        layout.addWidget( self.line_edit )
        
        edit_btn = QToolButton()
        edit_btn.setText( "BROWSE" )
        edit_btn.clicked[bool].connect( self.__btn_clicked )
        layout.addWidget( edit_btn )
        
        if self.info.inspector.is_optional:
            clear_btn = QToolButton()
            clear_btn.setText( "CLEAR" )
            clear_btn.clicked[bool].connect( self.__btn_clear_clicked )
            layout.addWidget( clear_btn )
        
        super().__init__( info, editor )
        
        self.line_edit.textChanged[str].connect( self.__text_changed )
        self.set_value( None )
    
    
    @exceptToGui()
    def __text_changed( self, _: str ):
        self.validated_value = self.convert_from_text( self.line_edit.text() )
    
    
    def convert_from_text( self, text ) -> object:
        raise NotImplementedError( "abstract" )
    
    
    def convert_to_text( self, value ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def browse_for_value( self, text ) -> Optional[str]:
        raise NotImplementedError( "abstract" )
    
    
    @exceptToGui()
    def __btn_clear_clicked( self, _ ):
        self.set_value( None )
    
    
    @exceptToGui()
    def __btn_clicked( self, _ ):
        result = self.browse_for_value( self.get_value() )
        
        if result is not None:
            self.set_value( result )
    
    
    def set_value( self, value: Optional[object] ):
        self.validated_value = value
        
        if value is None:
            self.line_edit.setText( "" )
        else:
            self.line_edit.setText( self.convert_to_text( value ) )
    
    
    def get_value( self ) -> Optional[object]:
        return self.validated_value


class Editor_Filename( Editor_BrowsableBase ):
    """
    Edits:  Filename[T, U] 
            Optional[Filename[T, U]]
    """
    
    
    def __init__( self, info: EditorInfo ):
        super().__init__( info, True )
    
    
    def browse_for_value( self, text ):
        d = QFileDialog()
        i = self.info  # type: EditorInfo
        t = cast(FileNameAnnotation, i.inspector.mannotation)
        
        if t.extension is not None:
            d.setNameFilters( ["{} files (*{})".format( t.extension[1:].upper(), t.extension )] )
        
        if t.mode == EFileMode.READ:
            d.setFileMode( QFileDialog.ExistingFile )
        else:
            d.setFileMode( QFileDialog.AnyFile )
        
        d.selectFile( text )
        
        if d.exec_():
            file_name = d.selectedFiles()[0]
            return file_name
    
    
    def convert_from_text( self, text ):
        try:
            return self.info.inspector.type_or_optional_type( text )
        except:
            return None
    
    
    def convert_to_text( self, value ):
        return str( value )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_mannotation_of( Filename )


class Editor_Flags( EditorBase ):
    """
    Edits: Flags
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QGroupBox()
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self.editor.setLayout( layout )
        # noinspection PyTypeChecker
        self.items = list( info.inspector.type_or_optional_type )
        control_lookup = { }
        self.cbs = []
        
        for enum_item in self.items:
            sub_editor = QCheckBox()
            sub_editor.setProperty( "xeditor", enum_item )
            layout.addWidget( sub_editor )
            sub_editor.setText( enum_item.name )
            control_lookup[enum_item] = sub_editor
            self.cbs.append( sub_editor )
        
        spacerItem = QSpacerItem( 20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum )
        layout.addItem( spacerItem )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_direct_sub_class( Flags )
    
    
    def set_value( self, value ):
        for x in self.cbs:
            if x.property( "xeditor" ) == value:
                x.setChecked( True )
            else:
                x.setChecked( False )
    
    
    def get_value( self ):
        for x in self.cbs:
            if x.isChecked():
                return x.property( "xeditor" )


class Editor_Bool( EditorBase ):
    """
    Edits:  bool
            Optional[bool]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.option_align_left = info.messages.get( constants.OPTION_ALIGN_LEFT, False )
        self.option_radio = info.messages.get( constants.OPTION_BOOLEAN_RADIO, False )
        self.option_texts = info.messages.get( constants.OPTION_BOOLEAN_TEXTS, ("", "", "") )
        
        # Create frame
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self.editor = QFrame()
        self.editor.setLayout( layout )
        
        if self.option_radio:
            self.using_radio = True
            self.radio_yes = QRadioButton()
            self.radio_yes.setText( self.option_texts[0] or "True" )
            self.radio_no = QRadioButton()
            self.radio_no.setText( self.option_texts[1] or "False" )
            editors = (self.radio_yes, self.radio_no)
            
            if info.inspector.is_optional:
                self.radio_neither = QRadioButton()
                self.radio_neither.setText( self.option_texts[2] or "None" )
                editors += self.radio_neither
            else:
                self.radio_neither = None
        else:
            self.using_radio = False
            self.check_box = QCheckBox()
            self.check_box.stateChanged[int].connect( self.__on_checkbox_stateChanged )
            
            if info.inspector.is_optional:
                self.check_box.setTristate( True )
            
            editors = (self.check_box,)
        
        for editor in editors:
            layout.addWidget( editor )
            
            if not self.option_align_left:
                editor.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        
        if self.option_align_left:
            layout.addItem( QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Ignored ) )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_type_or_optional_type_subclass( bool )
    
    
    @exceptToGui()
    def __on_checkbox_stateChanged( self, state: int ):
        if state == Qt.PartiallyChecked:
            self.check_box.setText( self.option_texts[2] )
        elif state == Qt.Checked:
            self.check_box.setText( self.option_texts[0] )
        else:
            self.check_box.setText( self.option_texts[1] )
    
    
    def set_value( self, value: Optional[object] ) -> None:
        if self.using_radio:
            if value is None:
                if self.radio_neither is not None:
                    self.radio_neither.setChecked( True )
                else:
                    self.radio_yes.setChecked( False )
                    self.radio_no.setChecked( False )
            elif value:
                self.radio_yes.setChecked( True )
            else:
                self.radio_no.setChecked( True )
        else:
            if value is None:
                self.check_box.setCheckState( Qt.PartiallyChecked )
            elif value:
                self.check_box.setChecked( Qt.Checked )
            else:
                self.check_box.setChecked( Qt.Unchecked )
            
            self.__on_checkbox_stateChanged( self.check_box.checkState() )
    
    
    def get_value( self ) -> Optional[bool]:
        if self.using_radio:
            if self.radio_yes.isChecked():
                return True
            elif self.radio_no.isChecked():
                return True
            else:
                return None
        else:
            x = self.check_box.checkState()
            
            if x == Qt.PartiallyChecked:
                return None
            elif x == Qt.Checked:
                return True
            elif x == Qt.Unchecked:
                return False
            else:
                raise SwitchError( "self.editor.checkState()", x )


class Editor_Float( EditorBase ):
    """
    Edits:  float
    """
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return issubclass( info.inspector.value, float )
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        self.editor.setValidator( QDoubleValidator() )
        super().handle_changes( self.editor.textChanged[str] )
        super().__init__( info, self.editor, )
        self.set_value( None )
    
    
    def set_value( self, value ):
        self.editor.setText( str( value ) )
    
    
    def get_value( self ):
        text = self.editor.text()
        
        if not text:
            return None
        
        try:
            return self.info.inspector.value( text )
        except:
            return None


class Editor_Int( EditorBase ):
    """
    Edits:  int
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QSpinBox()
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_direct_sub_class( int )
    
    
    def set_value( self, value: object ) -> None:
        self.editor.setValue( value )
    
    
    def get_value( self ) -> int:
        return self.editor.value()


class Editor_ReadOnly( EditorBase ):
    """
    Edits:  flags.READ_ONLY
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        self.editor.setReadOnly( True )
        super().__init__( info, self.editor )
        self.value = None
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_mannotation_of( HReadonly )
    
    
    def set_value( self, value ):
        self.value = value
        self.editor.setText( str( value ) )
    
    
    def get_value( self ):
        return self.value
