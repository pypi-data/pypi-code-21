"""
Functions for formatting stuff using ANSI codes and/or esoteric UNICODE characters.
"""

from typing import Union, Iterable

from colorama import Back, Fore, Style

from mhelper import ansi, ansi_helper, exception_helper, string_helper


def format_source( text: str,
                   keywords: Iterable[str],
                   variables: Iterable[str] ) -> str:
    """
    Prints source text, highlighting keywords and variables, and prefixing line numbers
    
    :param text:        Text to print
    :param keywords:    Keywords to highlight
    :param variables:   Variables to highlight
    :return:            Nothing
    """
    r = []
    
    text = text.split( "\n" )
    
    for i, line in enumerate( text ):
        prefix = Back.LIGHTBLACK_EX + Fore.BLACK + " " + str( i ).rjust( 4 ) + " " + Style.RESET_ALL + " "
        
        line = string_helper.highlight_words( line, keywords, Style.RESET_ALL + Fore.GREEN, Style.RESET_ALL )
        line = string_helper.highlight_words( line, variables, Style.RESET_ALL + Fore.CYAN, Style.RESET_ALL )
        
        r.append( prefix + line )
    
    return "\n".join( r )


def format_traceback( exception: Union[BaseException, str],
                      traceback_ = None,
                      warning = False,
                      wordwrap = 0 ) -> str:
    """
    Formats a traceback.
    
    :param exception:       Exception to display 
    :param traceback_:      Traceback text (leave as `None` to get the system traceback) 
    :param warning:         Set to `True` to use warning, rather than error, colours 
    :param wordwrap:        Set to the wordwrap width. 
    :return:                ANSI containing string  
    """
    r = []
    
    wordwrap = wordwrap or 120
    
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
        CODE = Style.RESET_ALL + Fore.CYAN + Style.DIM
        FILE_LINES = Style.RESET_ALL + Style.DIM + Fore.BLUE
        FILE_NAMES = Style.BRIGHT + Fore.YELLOW
    
    r.append( PREFIX + "┌" + "─" * (wordwrap - 2) + "┐" + Style.RESET_ALL )
    
    if isinstance( exception, BaseException ):
        ex = exception
        
        while ex:
            if ex is not exception:
                r.append( PREFIX + "│" + MAIN_LINE + " " + "---CAUSED BY---" + Style.RESET_ALL )
            
            r.append( PREFIX + "│" + MAIN_LINE + " *" + type( ex ).__name__ + "*" + Style.RESET_ALL )
            ex_text = MAIN_LINE + string_helper.highlight_quotes( str( ex ), "«", "»", MAIN_LINE_H, MAIN_LINE )
            
            for line in ansi_helper.wrap( ex_text, wordwrap ):
                r.append( PREFIX + "│" + MAIN_LINE + " " + line + Style.RESET_ALL )
            
            ex = ex.__cause__
    
    else:
        r.append( str( exception ) )
    
    if not traceback_:
        traceback_ = exception_helper.full_traceback()
    
    lines = traceback_.split( "\n" )
    
    for i, line in enumerate( lines ):
        print_line = line.strip()
        prefix = PREFIX + "│" + Style.RESET_ALL + " "
        
        if print_line.startswith( "File " ):
            print_line = FILE_LINES + string_helper.highlight_regex( print_line, "\\/([^\\/]*)\"", FILE_NAMES, FILE_LINES )
            print_line = FILE_LINES + string_helper.highlight_regex( print_line, "line ([0-9]*),", FILE_NAMES, FILE_LINES )
            print_line = FILE_LINES + string_helper.highlight_regex( print_line, "in (.*)$", CODE, FILE_LINES )
            
            r.append( prefix + print_line + Style.RESET_ALL )
        elif line.startswith( " " ):
            r.append( prefix + "    " + CODE + ansi.ITALIC + print_line + Style.RESET_ALL )
        elif line.startswith( "*" ):
            c = wordwrap - len( print_line ) - 6
            r.append( PREFIX + "├────" + print_line + "─" * c + "┤" + Style.RESET_ALL )
        else:
            r.append( prefix + NORMAL + print_line + Style.RESET_ALL )
    
    r.append( PREFIX + "└" + "─" * (wordwrap - 2) + "┘" + Style.RESET_ALL )
    
    return "\n".join( r )


def format_two_columns( left_margin: int,
                        centre_margin: int,
                        right_margin: int,
                        left_text: str,
                        right_text: str ):
    """
    Formats a box.
    :param left_margin:     Width of left margin 
    :param centre_margin:   Width of centre margin 
    :param right_margin:    Width of right margin 
    :param left_text:       Text in left column 
    :param right_text:      Text in right column 
    :return: 
    """
    r = []
    left_space = centre_margin - left_margin - 1
    right_space = right_margin - centre_margin
    
    left_lines = list( ansi_helper.wrap( left_text, left_space ) )
    right_lines = list( ansi_helper.wrap( right_text, right_space ) )
    num_lines = max( len( left_lines ), len( right_lines ) )
    
    for i in range( num_lines ):
        left = left_lines[i] if i < len( left_lines ) else ""
        right = right_lines[i] if i < len( right_lines ) else ""
        
        text = (" " * left_margin) + ansi_helper.ljust( left, left_space, " " ) + Style.RESET_ALL + " " + right + Style.RESET_ALL
        r.append( text )
    
    return "\n".join( r )
