"""
Functions for dealing with ANSI strings.
"""
from typing import Iterator, cast, Optional, Iterable
import re

from collections import defaultdict

from mhelper import string_helper, SwitchError, exception_helper


_strip_ansi_rx = re.compile( r'(\x1b[^m]+m)' )
_AnsiStr_ = "AnsiStr"


class AnsiStr:
    """
    Manages an ANSI string as if it were a normal string.
    
    The codes are bound to prefix the characters before which they appear, hence where "#" are ANSI codes such as RED, BLUE, YELLOW, RESET...
    
    ```
    a = "#hello#.#world#"
    a[:8] == "#hello#.#wo"
    a[0] == "#h"
    a[1] == "e"
    a[-1] == "d#"
    ```
    
    The exception is any trailing code, which is bound after the last character.
    """
    
    
    def __init__( self, with_ansi: str ):
        exception_helper.assert_type( "with_ansi", with_ansi, str )
        
        self.with_ansi = with_ansi
        self.ansi_positions = defaultdict( str )
        
        elements = self.get_elements()
        
        texts = [elements[0]]
        c = len( elements[0] )
        
        for i in range( 1, len( elements ), 2 ):
            ansi = elements[i]
            
            self.ansi_positions[c] += ansi
            
            text = elements[i + 1]
            c += len( text )
            
            texts.append( text )
        
        self.without_ansi = "".join( texts )
        self.length = len( self.without_ansi )
    
    
    def __add__( self, other: str ) -> _AnsiStr_:
        if isinstance( other, str ):
            return AnsiStr( self.with_ansi + other )
        elif isinstance( other, AnsiStr ):
            return AnsiStr( self.with_ansi + other.with_ansi )
        else:
            raise SwitchError( "other", other, instance = True )
    
    
    def __mul__( self, other ):
        return AnsiStr( self.with_ansi * other )
    
    
    def get_elements( self ):
        return _strip_ansi_rx.split( self.with_ansi )
    
    
    def lstrip( self, chars: Optional[str] = None ) -> _AnsiStr_:
        remove = len( self.without_ansi ) - len( self.without_ansi.lstrip( chars ) )
        return self[remove:]
    
    
    def rstrip( self, chars: Optional[str] = None ) -> _AnsiStr_:
        remove = len( self.without_ansi ) - len( self.without_ansi.rstrip( chars ) )
        return self[:-remove]
    
    
    def strip( self, chars: Optional[str] = None ) -> _AnsiStr_:
        remove_left = len( self.without_ansi ) - len( self.without_ansi.lstrip( chars ) )
        remove_right = len( self.without_ansi ) - len( self.without_ansi.rstrip( chars ) )
        
        if remove_left + remove_right >= len( self ):
            return AnsiStr( "" )
        
        return self[remove_left:-remove_right]
    
    
    def join( self, others: Iterable[str] ):
        text = self.with_ansi.join( str( x ) for x in others )
        return AnsiStr( text )
    
    
    def __str__( self ):
        return self.with_ansi
    
    
    def __repr__( self ):
        return "".join( self )
    
    
    def __len__( self ):
        return self.length
    
    
    def __iter__( self ):
        for i in range( len( self ) ):
            ansi = self.ansi_positions.get( i ) or ""
            
            yield "{}_{}".format( repr( self.without_ansi[i] ), repr( ansi ) )
        
        ansi = self.ansi_positions.get( len( self ) ) or ""
        yield "_+{}".format( repr( ansi ) )
    
    
    def __getitem__( self, key ):
        if isinstance( key, slice ):
            r = []
            
            for i in range( key.start or 0, key.stop or len( self ), key.step or 1 ):
                r.append( self[i] )
            
            return AnsiStr( "" ).join( r )
        
        if key < 0:
            key += len( self )
        
        if key == len( self ) - 1:
            suffix = self.ansi_positions.get( key + 1 )
        else:
            suffix = ""
        
        prefix = self.ansi_positions.get( key ) or ""
        text = self.without_ansi[key]
        return AnsiStr( prefix + text + suffix )
    
    
    def wrap( self, width: int ) -> Iterator[_AnsiStr_]:
        return cast( Iterator[AnsiStr], string_helper.wrap( self._str, width ) )
    
    
    def ljust( self, width: int, char: str = None ) -> _AnsiStr_:
        return cast( AnsiStr, string_helper.ljust( self._str, width, self.__spacer( char )._str ) )
    
    
    def rjust( self, width: int, char: str = None ) -> _AnsiStr_:
        return cast( AnsiStr, string_helper.rjust( self._str, width, self.__spacer( char )._str ) )
    
    
    def cjust( self, width: int, char: str = None ) -> _AnsiStr_:
        return cast( AnsiStr, string_helper.cjust( self._str, width, self.__spacer( char )._str ) )
    
    
    def fix_width( self, width: int, char: str = None, justify : int = None ) -> _AnsiStr_:
        return cast( AnsiStr, string_helper.fix_width( self._str, width, self.__spacer( char )._str, justify ) )
    
    
    @property
    def _str( self ) -> str:
        return cast( str, self )
    
    
    @classmethod
    def __spacer( cls, char: str ) -> _AnsiStr_:
        if char is None:
            return _SPACE
        elif isinstance( char, AnsiStr ):
            return char
        else:
            return AnsiStr( char )


_SPACE = AnsiStr( " " )


def without_ansi( text: str ) -> str:
    return AnsiStr( text ).without_ansi


def length( text: str ) -> int:
    return len( AnsiStr( text ) )


def wrap( text: str, width: int ) -> Iterator[str]:
    return (str( x ) for x in AnsiStr( text ).wrap( width ))


def ljust( text: str, width: int, char = None ) -> str:
    return str( AnsiStr( text ).ljust( width, char ) )


def rjust( text: str, width: int, char = None ) -> str:
    return str( AnsiStr( text ).rjust( width, char ) )


def cjust( text: str, width: int, char: str = None ) -> str:
    return str( AnsiStr( text ).cjust( width, char ) )


def fix_width( text: str, width: int, char: str = None, justify : int = None ) -> str:
    return str( AnsiStr( text ).fix_width( width, char, justify ) )
