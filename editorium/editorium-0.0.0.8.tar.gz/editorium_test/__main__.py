import sys
from enum import Enum
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGroupBox, QGridLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton, QSlider
from flags import Flags
from mhelper import Filename, AnnotationInspector

import editorium
from editorium.editorium_qt import Editorium, EditorBase, EditorInfo


editors = []


class MyClass:
    def __init__( self, value ):
        self.value = value
    
    
    def __str__( self ):
        return "MyClass:{}".format( self.value )


class CustomEditor( EditorBase ):
    def __init__( self, info: EditorInfo ) -> None:
        editor = QSlider()
        editor.setOrientation( Qt.Horizontal )
        super().__init__( info, editor )
    
    
    def set_value( self, value: Optional[MyClass] ):
        if value is None:
            self.editor.setValue( 0 )
        else:
            self.editor.setValue( value.value )
    
    
    def get_value( self ) -> Optional[object]:
        return MyClass( self.editor.value() )
    
    
    @classmethod
    def can_handle( cls, info: EditorInfo ) -> bool:
        return info.inspector.value is MyClass


class MyEnum( Enum ):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class MyFlags( Flags ):
    ONE = 1
    TWO = 2
    FOUR = 4
    EIGHT = 8


def main():
    application = QApplication( sys.argv )
    
    window = QMainWindow()
    window.resize( 1024, 768 )
    window.setWindowTitle( "Editorium Test" )
    
    group = QGroupBox()
    window.setCentralWidget( group )
    
    layout = QGridLayout()
    group.setLayout( layout )
    
    e: Editorium = editorium.default_editorium()
    e.register( CustomEditor )
    
    types = ((int, 5),
             (float, 5.5),
             (str, "5"),
             (bool, True),
             (MyEnum, MyEnum.TWO),
             (MyFlags, (MyFlags.TWO | MyFlags.FOUR)),
             (Optional[int], 5),
             (Optional[float], 5.5),
             (Optional[str], "55"),
             (Optional[bool], True),
             (Optional[MyEnum], MyEnum.TWO),
             (Optional[MyFlags], (MyFlags.TWO | MyFlags.FOUR)),
             (Filename["r", ".txt"], "/blah/blah.txt"),
             (Filename["w", ".txt"], "/blah/blah.txt"),
             (Filename[".txt"], "/blah/blah.txt"),
             (Filename["r"], "/blah/blah.txt"),
             (Filename["w"], "/blah/blah.txt"),
             (MyClass, MyClass( 50 )),
             )
    
    messages = { }
    messages[editorium.OPTION_ALIGN_LEFT] = True
    messages[editorium.OPTION_BOOLEAN_RADIO] = True
    
    for i, (t, v) in enumerate( types ):
        label = QLabel()
        inspector = AnnotationInspector( t )
        label.setText( str( inspector ) )
        layout.addWidget( label, i, 0 )
        editor = e.get_editor( t, messages = messages )
        editor.set_value( v )
        layout.addWidget( editor.editor, i, 1 )
        vlabel = QLabel()
        layout.addWidget( vlabel, i, 2 )
        editors.append( (inspector, label, editor, vlabel) )
    
    spacer = QSpacerItem( 1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding )
    layout.addItem( spacer )
    
    button = QPushButton()
    button.setText( "Apply" )
    button.clicked[bool].connect( apply_all )
    layout.addWidget( button, i + 1, 0 )
    
    button = QPushButton()
    button.setText( "Update" )
    button.clicked[bool].connect( update_all )
    layout.addWidget( button, i + 1, 2 )
    
    window.show()
    
    application.exec_()


def update_all( _ ):
    __update_all( False )


def __update_all( apply ):
    for inspector, label, editor, vlabel in editors:
        assert isinstance( vlabel, QLabel )
        assert isinstance( inspector, AnnotationInspector )
        
        try:
            v = editor.get_value()
        except Exception as ex:
            v = ex
        
        vlabel.setText( "{} : <i>{}</i> <b>= {}</b>".format( type( editor ).__name__, type( v ).__name__, v ) )
        
        if isinstance( v, Exception ):
            vlabel.setStyleSheet( "color:#808000;" )
        elif not inspector.is_viable_instance( v ):
            vlabel.setStyleSheet( "color:red;" )
        else:
            vlabel.setStyleSheet( "color:blue;" )
            
            if apply:
                editor.set_value( v )


def apply_all( _ ):
    update_all( True )


if __name__ == "__main__":
    main()
