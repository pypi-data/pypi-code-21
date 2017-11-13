import re
import datetime
import warnings
from typing import Optional, List, Union, Callable, Iterable, cast
from collections import Counter

import os

from mhelper import array_helper


__strip_lines_rx = re.compile( r"^[ ]+", re.MULTILINE )


def first_words( t: str, min_length = 1 ) -> str:
    """
    Returns a string made up of the first and last words (optionally allows a min_length of first words)
    """
    result = ""
    last_iter = ""
    for match in re.finditer( r"[\w]+", t ):
        if len( match.group( 0 ) ) <= 1:
            continue
        
        last_iter = match.group( 0 )
        
        if len( result ) < min_length:
            if result:
                result += " "
            result += last_iter
            last_iter = None
    if result:
        if last_iter:
            return result + " " + last_iter
        else:
            return result
    else:
        return t


def first_word( t: str ) -> str:
    """
    Returns the first word from the string
    """
    match = re.match( r"[\w]+", t )
    
    if not match:
        return t
    
    return match.group( 0 )


def time_to_string( time: float ) -> str:
    """
    Given a time in seconds, returns an approximate string representation like "5 seconds", "4 minutes", etc.
    """
    if time <= 1.5:
        return str( round( time * 1000 ) ) + " milliseconds"
    
    if time < 60:
        return str( round( time ) ) + " seconds"
    
    time /= 60
    
    if time < (60 * 2):
        return str( round( time ) ) + " minutes"
    
    time /= 60
    
    return str( round( time ) ) + " hours"


def time_to_string_short( time: float, delimiter: str = ":" ) -> str:
    """
    Given a time in seconds, returns a formatted string like "00:05", or "02:01:05".
    """
    SECONDS_IN_ONE_HOUR = 60 * 60
    SECONDS_IN_ONE_MINUTE = 60
    
    hours = time // SECONDS_IN_ONE_HOUR
    time -= hours * SECONDS_IN_ONE_HOUR
    
    minutes = time // SECONDS_IN_ONE_MINUTE
    time -= minutes * SECONDS_IN_ONE_MINUTE
    
    seconds = time
    
    h_text = ""
    
    if hours:
        h_text = str( int( hours ) ) + delimiter
    
    m_text = str( int( minutes ) ).rjust( 2, "0" ) + delimiter
    
    s_text = str( int( seconds ) ).rjust( 2, "0" )
    
    return h_text + m_text + s_text


def highlight_words( text: str, words, colour, normal ):
    text = normal + text
    
    for x in words:
        text = highlight_regex( text, "/\b($" + x + ")\b/i", colour, normal )
    
    return text


def highlight_regex( text, regex, colour, normal, group = 1 ):
    l = len( colour ) + len( normal )
    
    for i, m in enumerate( re.finditer( regex, text, re.IGNORECASE ) ):
        s = m.start( group ) + l * i
        e = m.end( group ) + l * i
        
        text = text[:s] + colour + text[s:e] + normal + text[e:]
    
    return text


def highlight_quotes( text, start, end, colour, normal ):
    find = start + "([^" + start + end + "]+)" + end
    replace = colour + "\\1" + normal
    return re.sub( find, replace, text )


def curtail( text: str, start: Optional[str] = None, end: Optional[str] = None, error = False ):
    """
    Removes text from the start of end of a string
    """
    if start:
        if text.startswith( start ):
            text = text[len( start ):]
        elif error:
            raise KeyError( "Trying to remove the substring «{0}» from the string «{1}» but the string does not start with the substring.".format( start, text ) )
    
    if end:
        if text.endswith( end ):
            text = text[:len( text ) - len( end )]
        elif error:
            raise KeyError( "Trying to remove the substring «{0}» from the string «{1}» but the string does not end with the substring.".format( end, text ) )
    
    return text


def time_now() -> str:
    t = datetime.datetime.now()
    return t.strftime( '%Y-%m-%d %H:%M:%S' )


def percent( val ):
    val *= 100
    return "{0:.1f}%".format( val )


def timedelta_to_string( delta ) -> str:
    s = delta.seconds
    hours = s // 3600
    s -= hours * 3600
    minutes = s // 60
    seconds = s - (minutes * 60)
    
    if hours:
        return '%d:%02d:%02d' % (hours, minutes, seconds)
    else:
        return '%02d:%02d' % (minutes, seconds)


def fix_width( text: object, width: int = 20 ) -> str:
    return max_width( str( text ), width ).ljust( width )


def max_width( text: str, width: int = 20 ) -> str:
    if not isinstance( text, str ):
        warnings.warn( "max_width expects a `str` but got a «{}»".format( type( text ) ) )
        text = str( text )
    
    if width <= 1:
        warnings.warn( "Did you really mean to pass <width = {}> to max_width?".format( width ) )
    
    text = text.strip()
    
    if "\n" in text:
        text = text[:text.index( "\n" )]
    
    if len( text ) > width:
        text = text[:(width - 1)] + "…"
    
    assert len( text ) <= width
    return text


def size_to_string( size: int ):
    """
    Returns a `size`, specified in bytes, as a human-readable string, similar to `ls -h` in bash.
    """
    if size == -1:
        return "?"
    
    if size < 1024:
        return "{0:.1f}b".format( size )
    
    size /= 1024
    
    if size < 1024:
        return "{0:.1f}kb".format( size )
    
    size /= 1024
    
    if size < 1024:
        return "{0:.1f}Mb".format( size )
    
    size /= 1024
    
    return "{0:.1f}Gb".format( size )


def summarised_join( source: Counter, delimiter ):
    r = []
    
    for k, v in sorted( source.items(), key = lambda x: -x[1] ):
        r.append( "{1} × {0}".format( k, v ) )
    
    return delimiter.join( r )


def is_int( x ):
    if not x:
        return False
    
    try:
        _ = int( x )
        return True
    except:
        return False


def bulk_replace( text, format = "<*>", **kwargs ):
    for k, v in kwargs.items():
        text = text.replace( format.replace( "*", k ), v )
    
    return text


__make_name_regex = re.compile( "[^0-9a-zA-Z.]" )


def make_name( name ):
    return __make_name_regex.sub( "_", name )


def strip_lines( text ):
    return __strip_lines_rx.sub( "", text )


def prefix_lines( text, prefix, suffix = "" ):
    return prefix + text.replace( "\n", suffix + "\n" + prefix ) + suffix


def remove_prefix( text, prefix ) -> str:
    if not text.startswith( prefix ):
        raise ValueError( "I've been asked to remove a prefix «{0}» from a string «{1}», but the string doesn't start with that prefix.".format( prefix, text ) )
    
    return text[len( prefix ):]


def type_name( value ):
    return type( value ).__name__


def undo_camel_case( text: str, sep = " " ):
    result = []
    
    for i, c in enumerate( text ):
        if i and c.isupper():
            result.append( sep )
        
        result.append( c )
    
    return "".join( result )


def name_index( names: List[str], name: str ) -> int:
    """
    Given a `name`, finds its index in `names`. `name` can be a `str`, an `int` or an int as a str.
    :param names: List of names 
    :param name:  Name or index to find 
    :return: Index
    :exception ValueError: Not found
    """
    if isinstance( name, int ):
        v = name
    elif not isinstance( name, str ):
        raise TypeError( "`name` should be an `int` or a `str`, but it is «{0}» which is a {1}.".format( name, type_name( name ) ) )
    elif all( str.isdigit( x ) for x in name ):
        v = int( name )
    else:
        v = None
    
    if v is not None and 0 <= v < len( names ):
        return v
    
    if name in names:
        return names.index( name )
    
    raise ValueError( "Trying to find the column with header «{0}» but that column doesn't exist or is out of range. The columns are: {1}".format( name, names ) )


def list_to_string( list, sep = ", ", format = "{0}" ):
    return format.format( sep.join( str( x ) for x in list ) )


def current_time():
    import time
    return time.strftime( "%Y-%m-%d %H:%M:%S %z" )


def ordinal( i: object ):
    """
    Returns "1st", "2nd", "3rd", etc. from 1, 2, 3, etc.
    `i` can be anything coercible to a string that looks like a number.
    """
    i = str( i )
    l = i[-1]
    
    if l == "1":
        return i + "st"
    elif l == "2":
        return i + "nd"
    elif l == "3":
        return i + "rd"
    else:
        return i + "th"


def get_indent( line ):
    num_spaces = 0
    for x in line:
        if x == " ":
            num_spaces += 1
        else:
            return num_spaces
    
    return num_spaces


def remove_indent( current_indent, line: str ):
    i = 0
    
    for i, x in enumerate( line ):
        if x != " ":
            break
    
    i = min( i, current_indent )
    
    return line[i:]


def capitalise_first_and_fix( text: Optional[object], swap = "_-" ) -> str:
    text = capitalise_first( text )
    
    for x in swap:
        text = text.replace( x, " " )
    
    return text


def capitalise_first( text: Optional[object] ) -> str:
    if text is None:
        return ""
    
    text = str( text )
    
    if not text:
        return text
    
    if len( text ) == 1:
        return text[0].upper()
    
    return text[0].upper() + text[1:]


def special_to_symbol( value ):
    return value.replace( "\n", "␊" ).replace( "\r", "␍" ).replace( "\t", "␉" )


def unescape( v ):
    try:
        return v.encode().decode( "unicode_escape" )
    except Exception as ex:
        raise ValueError( "Unescape «{}» failed.".format( v ) ) from ex


def to_bool( x ):
    try:
        y = float( x )
        return y != 0
    except:
        x = x.lower()
        if x in ("true", "yes", "t", "y", "1", "on"):
            return True
        elif x in ("false", "no", "f", "n", "0", "off"):
            return False
        else:
            raise ValueError( "Cannot convert «{}» to boolean.".format( x ) )


DPrint = Callable[[object], None]


class FindError( Exception ):
    pass


def find( *,
          source: Iterable[object],
          search: str,
          namer: Optional[Union[Callable[[object], str], Callable[[object], List[str]]]] = None,
          detail: Optional[str] = None,
          fuzzy: Optional[bool] = True ):
    """
    Finds the command or plugin with the closest name to "text".
    
    :param source:  Source list 
    :param search:  Text to find 
    :param namer:   How to translate items in the source list, each item can translate to a `str`, or a `list` or `tuple` of `str` 
    :param detail:  What to call the collection in error messages.
    :param fuzzy:   Permit partial (start-of-word) matches
    :return:        The matching item in `source`
    :except FindError: The text was not matched 
    """
    
    #
    # Arguments
    #
    if not isinstance( source, list ) and not isinstance( source, tuple ):
        source = list( source )
    
    if not isinstance( search, str ):
        raise TypeError( "string_helper.find() takes a `str` and not a {} (`{}`).".format( type( search ).__name__, search ) )
    
    if namer is None:
        namer = cast( Callable[[object], str], str )
    
    
    def __get_names( item ):
        r = namer( item )
        
        if isinstance( r, str ):
            return [r]
        elif isinstance( r, list ) or isinstance( r, tuple ):
            return r
        else:
            raise TypeError( "Return value of namer «{}».".format( namer ) )
    
    
    #
    # Exact match
    #
    for item in source:
        for name in __get_names( item ):
            if search == name:
                return item
    
    #
    # Start-of-word match
    #
    if fuzzy:
        match_items = set()
        match_names = set()
        
        for item in source:
            for name in __get_names( item ):
                if name.startswith( search ):
                    match_items.add( item )
                    match_names.add( name )
        
        if len( match_items ) == 1:
            return array_helper.first( match_items )
    else:
        match_items = set()
    
    #
    # Failure
    #
    if detail is None:
        detail = "item"
    
    if not match_items:
        ss = []
        ss.append( "No such {}: «{}»".format( detail, search ) )
        available = []
        
        for item in source:
            for name in __get_names( item ):
                if name:
                    available.append( name )
        
        ss.append( "Options: " + ", ".join( "«{}»".format( x ) for x in available ) )
        
        raise FindError( "\n".join( ss ) )
    
    ss = []
    ss.append( "Ambiguous {} name: «{}»".format( detail, search ) )
    ss.append( "    ...did you mean..." )
    for item in match_items:
        for name in __get_names( item ):
            ss.append( "    ...... " + name.replace( search, "«" + search + "»" ) )
    
    raise FindError( "\n".join( ss ) )


def no_emoji( x ):
    return x + "\uFE0E"


def fix_indents( text: str ) -> str:
    text = str( text )
    lines = text.split( "\n" )
    lines[0] = lines[0].lstrip()
    
    if len( lines ) == 1:
        return lines[0]
    
    min_leading = 9999
    
    for line in lines[1:]:
        stripped = line.lstrip()
        
        if stripped:
            leading = len( line ) - len( stripped )
            min_leading = min( leading, min_leading )
    
    if min_leading == 9999:
        return text.strip()
    
    for i in range( 1, len( lines ) ):
        lines[i] = lines[i][min_leading:]
    
    return "\n".join( lines )


def assert_unicode():
    """
    UTF-8 check. Probably Windows Console Services is badly configured.
    """
    UNICODE_ERROR_MESSAGE = \
        """


        +-------------------------------------------------------------------------------------------------------+--------+
        | UNICODE ENCODE ERROR                                                                                  |        |
        +-------------------------------------------------------------------------------------------------------+  X  X  +
        | It looks like your console doesn't support Unicode.                                                   |        |
        |                                                                                                       |  _--_  |
        | intermake needs Unicode to display its UI.                                                             |        |
        | Python doesn't seem to know your terminal doesn't support UTF8 and just crashes :(                    +--------|
        | This problem usually occurs when using cmd.exe on Windows.                                                     |
        |                                                                                                                |
        | On Windows, you could `set PYTHONIOENCODING=ascii:replace` as a quick fix, but it might be better in the long  |
        | run to setup your console and font to support UTF8: https://stackoverflow.com/questions/379240                 |
        |                                                                                                                |
        | On Unix, the quick fix is `export PYTHONIOENCODING=ascii:replace`                                              |
        +----------------------------------------------------------------------------------------------------------------+


        """
    try:
        print( "😁\r \r", end = "" )
    except UnicodeEncodeError as ex:
        # On the plus side, Window's Console has a horizontal scroll bar, so we can display an over-sized error message without it breaking...
        raise ValueError( UNICODE_ERROR_MESSAGE ) from ex
    
    colorterm = os.environ.get( "COLORTERM" )
    
    if colorterm is None:
        warnings.warn( "COLORTERM environment variable not set. Use a terminal supporting true colour." )


def centre_align( text, width, char = " ", prefix = None, suffix = None ):
    """
    Centre aligns text.
    :param suffix:  Prefix to use in output. e.g. colour codes that shouldn't be considered as part of the length.
    :param prefix:  Suffix to use in output. e.g. colour codes that shouldn't be considered as part of the length.
    :param text:    Text to align 
    :param width:   Width to align into 
    :param char:    Padding character
    :return:        Aligned text. 
    """
    
    use = text
    
    if prefix:
        use = prefix + use
    
    if suffix:
        use = use + suffix
    
    length = len( text )
    
    pad_len = (width - length) // 2 - 1
    pad = char * pad_len
    
    if (length % 2) != 0:
        return pad + use + pad + char
    else:
        return pad + use + pad
