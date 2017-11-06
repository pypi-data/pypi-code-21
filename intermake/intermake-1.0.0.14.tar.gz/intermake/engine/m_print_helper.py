"""
Functions for printing things (usually to the console)
"""

import re
import textwrap
import traceback

from typing import Optional, Iterator, Union, Callable

from colorama import Back, Fore, Style

from mhelper import string_helper, ansi


class SetupError( Exception ):
    def __init__( self, name, value ):
        super().__init__( "Setup error - the setting «{}»=«{}» is invalid. Did you meant to configure the setting first?".format( name, value ) )


def print_source( text, keywords, variables, destination = None ):
    """
    Prints source text (highlighting keywords)
    :param destination: Where to print to (default is `print`).
    :param text:        Text to print
    :param keywords:    Keywords to highlight
    :param variables:   Variables to highlight
    :return:            Nothing
    """
    if destination is None:
        destination = print
    
    text = text.split( "\n" )
    
    for i, line in enumerate( text ):
        prefix = Back.LIGHTBLACK_EX + Fore.BLACK + " " + str( i ).rjust( 4 ) + " " + Style.RESET_ALL + " "
        
        line = string_helper.highlight_words( line, keywords, Style.RESET_ALL + Fore.GREEN, Style.RESET_ALL )
        line = string_helper.highlight_words( line, variables, Style.RESET_ALL + Fore.CYAN, Style.RESET_ALL )
        
        if destination is not None:
            destination( prefix + line )


def wrap( text, width = 70 ) -> Iterator[str]:
    """
    Wraps text, accounting for colour codes
    :param text:   Text to wrap 
    :param width:  Width to wrap to 
    :return:       Wrapped text
    """
    if width <= 0:
        for line in str( text ).split( "\n" ):
            yield line
        
        return
    
    for line in str( text ).split( "\n" ):
        chunks = textwrap.TextWrapper.wordsep_simple_re.split( line )
        cur_line = ""
        cur_len = 0
        
        if len( chunks ) == 1:
            yield chunks[0]
            continue
        
        for chunk in chunks:
            chunk_len = ansi_len( chunk )
            
            if chunk_len > width:
                # TOO LONG!
                while chunk:
                    fit = (width - cur_len)
                    cur_line += chunk[:fit]
                    chunk = chunk[fit:]
                    cur_len += fit
                    
                    if cur_len == width:
                        yield cur_line
                        cur_line = ""
                        cur_len = 0
            elif cur_len + chunk_len > width:
                # BREAK
                yield cur_line
                cur_line = chunk
                cur_len = chunk_len
            else:
                # CONTINUE
                cur_line += chunk
                cur_len += chunk_len
        
        if cur_line:
            yield cur_line


def print_traceback( exception: Union[BaseException, str], traceback_ = None, warning = False, wordwrap = 0 ):
    """
    Prints a traceback to the output.
    """
    if warning:
        MAIN_LINE = Style.RESET_ALL + Back.YELLOW + Fore.BLACK
        MAIN_LINE_H = Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.BLACK
        PREFIX = Back.LIGHTYELLOW_EX + Fore.BLACK
        NORMAL = Fore.CYAN
        CODE = Fore.CYAN + Style.DIM
        FILE_LINES = Style.DIM + Fore.CYAN
        FILE_NAMES = Fore.LIGHTCYAN_EX
    else:
        MAIN_LINE = Style.RESET_ALL + Back.RED + Fore.LIGHTWHITE_EX
        MAIN_LINE_H = ansi.RESET + ansi.BOLD + ansi.BACK_RED + ansi.FORE_BRIGHT_WHITE + ansi.ITALIC
        PREFIX = Back.LIGHTRED_EX + Fore.BLACK
        NORMAL = Fore.CYAN
        CODE = Fore.CYAN + Style.DIM
        FILE_LINES = Style.DIM + Fore.BLUE
        FILE_NAMES = Style.BRIGHT + Fore.YELLOW
    
    if isinstance( exception, BaseException ):
        msg = []
        ex = exception
        
        while ex:
            msg.append( str( ex ) )
            ex = ex.__cause__
        
        ex_text = ("\n" + NORMAL + "---CAUSED BY---" + MAIN_LINE + "\n").join( msg )
    else:
        ex_text = str( exception )
    
    ex_text = MAIN_LINE + string_helper.highlight_quotes( ex_text, "«", "»", MAIN_LINE_H, MAIN_LINE  )
    
    for line in wrap( ex_text, wordwrap ):
        print( MAIN_LINE + line + Style.RESET_ALL )
    
    if not traceback_:
        traceback_ = traceback.format_exc()
    
    lines = traceback_.split( "\n" )
    
    for i, line in enumerate( lines ):
        prefix = PREFIX + " " + str( i ).rjust( 2 ) + " " + Style.RESET_ALL + " "
        
        if line.startswith( "  File" ):
            line = FILE_LINES + string_helper.highlight_regex( line, "\\/([^\\/]*)\"", FILE_NAMES, FILE_LINES )
            line = FILE_LINES + string_helper.highlight_regex( line, "line ([0-9]*),", FILE_NAMES, FILE_LINES )
            line = FILE_LINES + string_helper.highlight_regex( line, "in (.*)$", FILE_NAMES, FILE_LINES )
            
            print( prefix + line + Style.RESET_ALL )
        elif line.startswith( "    " ):
            print( prefix + CODE + line + Style.RESET_ALL )
        else:
            print( prefix + NORMAL + line + Style.RESET_ALL )
    
    print( Style.RESET_ALL )


def display_error( owner, text: str, exception: Optional[Exception] = None, traceback_: Optional[str] = None ):
    """
    Displays an error in a message-box
    :param text:          Error text
    :param exception:     Exception (optional)
    :param traceback_:    Traceback (optional)
    :type owner: QWidget
    """
    from PyQt5.QtWidgets import QMessageBox
    msg = QMessageBox( owner )
    msg.setIcon( QMessageBox.Critical )
    msg.setText( text )
    
    if exception:
        print( str( exception ) )
        print( traceback_ )
        msg.setInformativeText( str( exception ) )
        msg.setDetailedText( traceback_ )
    msg.exec_()


def __just( just_function, text: object, char: str, length: int ) -> str:
    """
    Justifies text, but also truncates it if it's too long
    
    :param just_function:  Justification function 
    :param text:           Text to justify
    :param char:           Character to use for padding
    :param length:         Length to justify within
    :return:               Justified text
    """
    if length <= 0:
        return ""
    
    text = str( text )
    
    if "\n" in text:
        text = text[:text.index( "\n" )]
    
    if len( text ) > length:
        text = text[0:(length - 1)] + "…"
    
    return just_function( text, char, length )


__strip_ansi_rx = re.compile( r'\x1b[^m]*m' )


def strip_ansi( text: str ) -> str:
    return __strip_ansi_rx.sub( "", text )


def ansi_ljust( text: str, char: str, length: int ) -> str:
    needed = length - ansi_len( text )
    return text + char * needed


def ansi_rjust( text: str, char: str, length: int ) -> str:
    needed = length - ansi_len( text )
    return char * needed + text


def ansi_len( text: str ) -> int:
    return len( strip_ansi( text ) )


def ljust( text: object, char: str, length: int ) -> str:
    return __just( ansi_ljust, text, char, length )


def rjust( text: object, char: str, length: int ) -> str:
    return __just( ansi_rjust, text, char, length )


def cjust( text: object, char: str, length: int ) -> str:
    text = str( text )
    j = __just( ansi_rjust, text, char, length // 2 + ansi_len( text ) // 2 )
    return ansi_ljust( j, char, length )


DPrint = Callable[[str], None]


def print_box( print: DPrint, left_margin: int, centre_margin: int, right_margin: int, left_text: str, right_text: str ):
    left_space = centre_margin - left_margin - 1
    right_space = right_margin - centre_margin
    
    left_lines = list( wrap( left_text, left_space ) )
    right_lines = list( wrap( right_text, right_space ) )
    num_lines = max( len( left_lines ), len( right_lines ) )
    
    for i in range( num_lines ):
        left = left_lines[i] if i < len( left_lines ) else ""
        right = right_lines[i] if i < len( right_lines ) else ""
        
        text = (" " * left_margin) + ansi_ljust( left, " ", left_space ) + Style.RESET_ALL + " " + right + Style.RESET_ALL
        print( text )
