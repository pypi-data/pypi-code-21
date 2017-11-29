import sip
from enum import Enum
from typing import Dict, Optional, cast, Sequence, List, Iterable, Type

from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QSpacerItem, QSpinBox, QToolButton, QWidget, QRadioButton, QMessageBox
from flags import Flags

from mhelper import SwitchError, abstract, exceptToGui, override, EFileMode, Filename, HReadonly, AnnotationInspector, FileNameAnnotation, virtual

from editorium import constants


def __combine( x: Dict[Flags, QCheckBox] ) -> Flags:
    t = next( iter( x.keys() ) )
    # noinspection PyUnresolvedReferences
    value = t.__no_flags__
    
    for k, v in x:
        if v.isChecked():
            value |= k
    
    return value


class EditorInfo:
    def __init__( self, editorium: "Editorium", type_, messages: Dict[object, object] ) -> None:
        self.editorium = editorium
        self.inspector = AnnotationInspector( type_ )
        self.messages = messages
    
    
    def __str__( self ):
        return str( self.inspector )


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
        
        :param info: Contains the type information
        """
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> Optional[object]:
        """
        Obtains the value stored in the editor.
        This method should generally return the correct type, though this is not guaranteed.
        This method may raise an exception if the user has made an invalid selection.
        
        :except Exception: Invalid selection 
        """
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: Optional[object] ):
        """
        Sets the value of the editor.
        
        :param value:   A value that commutes with `self.info`.
                        The value `None` should also always be accepted as a default.
        """
        raise NotImplementedError( "abstract" )
    
    
    def handle_changes( self, signal ) -> None:
        """
        Connects the specified `signal` to the __change_occurred handler.
        """
        signal.connect( self.__change_occurred )
    
    
    # noinspection PyUnusedLocal
    @exceptToGui()
    def __change_occurred( self, *args, **kwargs ) -> None:
        """
        Handles changes to the editor.
        """
        pass


class Editorium:
    """
    Holds the set of editors.
    
    :attr editors:              Array of editor types.
    :attr default_messages:     Always appended to `messages`. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.editors = []
        self.default_messages = { }
    
    
    def register( self, editor: Type[EditorBase] ):
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
        self.checkbox.stateChanged[int].connect( self.__on_checkbox_toggled )
        self.checkbox.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        
        self.option_visual_tristate = info.messages.get( constants.OPTION_VISUAL_TRISTATE, False )
        self.option_hide = info.messages.get( constants.OPTION_HIDE, False )
        self.option_show_text = info.messages.get( constants.OPTION_SHOW_TEXT, "" )
        self.option_hide_text = info.messages.get( constants.OPTION_HIDE_TEXT, self.option_show_text )
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
            self.checkbox.setText( self.option_show_text )
        elif self.option_hide:
            self.checkbox.setText( self.option_hide_text )
    
    
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
        self.sub_editor.set_value( value )


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
        return info.inspector.is_directly_below( str )
    
    
    def set_value( self, value: str ):
        if value is None:
            value = ""
        
        self.editor.setText( value )
    
    
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


class Editor_GenericList( EditorBase ):
    """
    Edits: List[T]
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.list_type = info.inspector.generic_list_type
        
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
    
    
    def __add_editor( self ) -> None:
        editor = self.info.editorium.get_editor( self.list_type )
        self.layout.addWidget( editor.editor )
        self.editors.append( editor )
    
    
    def __remove_editor( self ) -> None:
        editor = self.editors.pop()
        self.layout.removeWidget( editor.editor )
        sip.delete( editor.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_generic_list
    
    
    def set_value( self, value: List[object] ) -> None:
        self.spinner.setValue( len( value ) )
        
        for i, x in enumerate( value ):
            self.editors[i].set_value( x )
    
    
    def get_value( self ) -> List[object]:
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
        self.editor.setPlaceholderText( "(empty)" )
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return not info.inspector.is_optional
    
    
    def set_value( self, value: object ) -> None:
        self.editor.setText( str( value ) if value is not None else "" )
    
    
    def get_value( self ) -> str:
        return self.editor.text()


class Editor_EnumerativeBase( EditorBase ):
    """
    Base class for enumerative edits.
    """
    
    
    def __init__( self, info: EditorInfo ):
        self.editor: QComboBox = QComboBox()
        self.items: Sequence[object] = self.get_items( info )
        
        if info.inspector.is_optional:
            self.items: Sequence[object] = cast( List[object], [None] ) + list( self.items )
        
        self.names: List[str] = [self.get_none_name( info ) if x is None else self.get_name( info, x ) for x in self.items]
        self.editor.setEditable( False )
        
        self.editor.addItems( self.names )
        
        super().handle_changes( self.editor.currentIndexChanged[int] )
        
        super().__init__( info, self.editor )
        
        self.set_value( None )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_directly_below_or_optional( cls.get_type() )
    
    
    @classmethod
    def get_type( cls ) -> type:
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: object ):
        if value is None:
            if not self.info.inspector.is_optional:
                self.editor.setCurrentIndex( 0 )
                return
        
        self.editor.setCurrentIndex( self.items.index( value ) )
    
    
    def get_value( self ) -> object:
        if self.editor.currentIndex() == -1:
            if self.info.inspector.is_optional:
                return None
            else:
                raise ValueError( "A selection must be made." )
        
        return self.items[self.editor.currentIndex()]
    
    
    @virtual
    def get_none_name( self, info: EditorInfo ) -> str:
        return info.messages.get( str( constants.OPTION_ENUM_NONE ), "None" )
    
    
    @abstract
    def get_items( self, info: EditorInfo ) -> Sequence[object]:
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def get_name( self, info: EditorInfo, item: object ) -> str:
        raise NotImplementedError( "abstract" )


class Editor_Enum( Editor_EnumerativeBase ):
    """
    Edits:  Enum
            Optional[Enum]
    """
    
    
    @classmethod
    def get_type( cls ) -> type:
        return Enum
    
    
    def get_name( self, info: EditorInfo, item: object ) -> str:
        assert isinstance( item, Enum )
        return cast( Enum, item ).name
    
    
    def get_items( self, info: EditorInfo ) -> Sequence[object]:
        type_ = info.inspector.type_or_optional_type
        assert issubclass( type_, Enum )
        return list( type_ )


@abstract
class Editor_TextBrowsableBase( EditorBase ):
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
        
        if info.inspector.is_optional:
            clear_btn = QToolButton()
            clear_btn.setText( "CLEAR" )
            clear_btn.clicked[bool].connect( self.__btn_clear_clicked )
            layout.addWidget( clear_btn )
        
        super().__init__( info, editor )
        
        self.set_value( None )
    
    
    def on_convert_from_text( self, text: str ) -> object:
        raise NotImplementedError( "abstract" )
    
    
    def on_convert_to_text( self, value: object ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def on_browse( self, value: object ) -> Optional[str]:
        raise NotImplementedError( "abstract" )
    
    
    def on_get_default_value( self ) -> object:
        raise NotImplementedError( "abstract" )
    
    
    @exceptToGui()
    def __btn_clear_clicked( self, _ ) -> None:
        self.set_value( None )
    
    
    @exceptToGui()
    def __btn_clicked( self, _ ) -> None:
        try:
            value = self.on_convert_from_text( self.line_edit.text() )
        except Exception as ex:
            msg = QMessageBox()
            msg.setText( "Information" )
            msg.setIcon( QMessageBox.Information )
            msg.setInformativeText( str( ex ) )
            msg.exec_()
            value = self.on_get_default_value()
        
        result = self.on_browse( value )
        
        if result is not None:
            self.set_value( result )
    
    
    def set_value( self, value: Optional[object] ):
        if value is None:
            value = self.on_get_default_value()
        
        text = self.on_convert_to_text( value )
        self.line_edit.setText( text )
    
    
    def get_value( self ) -> Optional[object]:
        return self.on_convert_from_text( self.line_edit.text() )


class Editor_Filename( Editor_TextBrowsableBase ):
    """
    Edits:  Filename[T, U] 
            Optional[Filename[T, U]]
    """
    
    
    def on_get_default_value( self ) -> object:
        return ""
    
    
    def on_convert_from_text( self, text ) -> Optional[str]:
        return text
    
    
    def on_convert_to_text( self, value: Filename ) -> str:
        return value
    
    
    def __init__( self, info: EditorInfo ):
        super().__init__( info, True )
    
    
    def on_browse( self, value: Filename ) -> str:
        d = QFileDialog()
        i = self.info  # type: EditorInfo
        t = cast( FileNameAnnotation, i.inspector.mannotation )
        
        if t.extension is not None:
            d.setNameFilters( ["{} files (*{})".format( t.extension[1:].upper(), t.extension )] )
        
        if t.mode == EFileMode.READ:
            d.setFileMode( QFileDialog.ExistingFile )
        else:
            d.setFileMode( QFileDialog.AnyFile )
        
        d.selectFile( value )
        
        if d.exec_():
            file_name = d.selectedFiles()[0]
            return file_name
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_mannotation_of( Filename )


class Editor_EnumerativeMultiBase( EditorBase ):
    PROPERTY_NAME = "Editor_EnumerativeMultiBase_Value"
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self.editor.setLayout( layout )
        self.items = list( self.get_items( info ) )
        control_lookup = { }
        self.sub_editors = []
        
        for item in self.items:
            sub_editor = QCheckBox()
            sub_editor.setProperty( self.PROPERTY_NAME, item )
            layout.addWidget( sub_editor )
            sub_editor.setText( self.get_name( info, item ) )
            control_lookup[item] = sub_editor
            self.sub_editors.append( sub_editor )
        
        spacerItem = QSpacerItem( 20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum )
        layout.addItem( spacerItem )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def set_value( self, value: Flags ) -> None:
        for x in self.sub_editors:
            if self.is_set( self.info, x.property( self.PROPERTY_NAME ), value ):
                x.setChecked( True )
            else:
                x.setChecked( False )
    
    
    def is_set( self, info: EditorInfo, query: object, value: object ) -> bool:
        raise NotImplementedError( "abstract" )
    
    
    def get_value( self ) -> object:
        values = []
        for x in self.sub_editors:
            if x.isChecked():
                values.append( x.property( self.PROPERTY_NAME ) )
        
        return self.translate( self.info, values )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        raise NotImplementedError( "abstract" )
    
    
    def get_name( self, info: EditorInfo, item: object ) -> str:
        raise NotImplementedError( "abstract" )
    
    
    def translate( self, info: EditorInfo, values: List[object] ) -> object:
        raise NotImplementedError( "abstract" )


class Editor_Flags( Editor_EnumerativeMultiBase ):
    """
    Edits: Flags
    """
    
    
    def translate( self, info: EditorInfo, values: List[Flags] ) -> Flags:
        type_ = info.inspector.value
        
        result = type_( 0 )
        
        for value in values:
            result |= value
        
        return result
    
    
    def is_set( self, info: EditorInfo, query: Flags, value: Flags ) -> bool:
        return (value & query) == query
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_directly_below( Flags )
    
    
    def get_items( self, info: EditorInfo ) -> Iterable[object]:
        return cast( Iterable[Flags], info.inspector.type_or_optional_type )
    
    
    def get_name( self, info: EditorInfo, item: Flags ) -> str:
        return item.name


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
            editors = [self.radio_yes, self.radio_no]
            
            if info.inspector.is_optional:
                self.radio_neither = QRadioButton()
                self.radio_neither.setText( self.option_texts[2] or "None" )
                editors.append( self.radio_neither )
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
        
        self.set_value( None )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_directly_below_or_optional( bool )
    
    
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
                    self.radio_no.setChecked( True )
            elif value:
                self.radio_yes.setChecked( True )
            else:
                self.radio_no.setChecked( True )
        else:
            if value is None:
                if self.info.inspector.is_optional:
                    self.check_box.setCheckState( Qt.PartiallyChecked )
                else:
                    self.check_box.setChecked( Qt.Unchecked )
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
                return False
            elif self.info.inspector.is_optional:
                return None
            else:
                raise ValueError( "A selection must be made." )
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
        return info.inspector.value is float
    
    
    def __init__( self, info: EditorInfo ):
        self.editor = QLineEdit()
        self.editor.setPlaceholderText( "0" )
        self.editor.setValidator( QDoubleValidator() )
        super().handle_changes( self.editor.textChanged[str] )
        super().__init__( info, self.editor, )
        self.set_value( None )
    
    
    def set_value( self, value: Optional[float] ) -> None:
        self.editor.setText( str( value ) if value else "0" )
    
    
    def get_value( self ) -> Optional[float]:
        text = self.editor.text()
        
        if not text:
            return 0
        
        return float( text )


class Editor_Int( EditorBase ):
    """
    Edits:  int
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QSpinBox()
        self.editor.setMaximum( 2147483647 )
        
        super().__init__( info, self.editor )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ):
        return info.inspector.is_directly_below( int )
    
    
    def set_value( self, value: int ) -> None:
        if value is None:
            value = 0
        
        self.editor.setValue( value )
    
    
    def get_value( self ) -> int:
        return self.editor.value()


class Editor_ReadOnly( EditorBase ):
    """
    Edits:  flags.READ_ONLY
    """
    
    
    def __init__( self, info: EditorInfo ) -> None:
        self.editor = QLineEdit()
        self.editor.setReadOnly( True )
        super().__init__( info, self.editor )
        self.value = None
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.is_mannotation_of( HReadonly )
    
    
    def set_value( self, value: object ) -> None:
        self.value = value
        self.editor.setText( str( value ) )
    
    
    def get_value( self ) -> object:
        return self.value
