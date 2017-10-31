from random import randint

from PyQt5.QtGui import QColor, QPen, QBrush


class Colours:
    BLACK            = QColor( 0, 0, 0 )
    DARK_GRAY        = QColor( 64, 64, 64 )
    GRAY             = QColor( 128, 128, 128 )
    LIGHT_GRAY       = QColor( 192, 192, 192 )
    WHITE            = QColor( 255, 255, 255 )
    
    RED              = QColor( 255, 0, 0 )
    GREEN            = QColor( 0, 255, 0 )
    BLUE             = QColor( 0, 0, 255 )
    
    CYAN             = QColor( 0, 255, 255 )
    MAGENTA          = QColor( 255, 0, 255 )
    YELLOW           = QColor( 255, 255, 0 )
    
    ORANGE           = QColor( 255, 128, 0 )
    FUSCHIA          = QColor( 255, 0, 128 )
    LIME             = QColor( 128, 255, 0 )
    SPRING_GREEN     = QColor( 0, 255, 128 )
    PURPLE           = QColor( 128, 0, 255 )
    DODGER_BLUE      = QColor( 128, 0, 255 )
    
    DARK_RED         = QColor( 128, 0, 0 )
    DARK_GREEN       = QColor( 0, 128, 0 )
    DARK_BLUE        = QColor( 0, 0, 128 )
    
    DARK_CYAN        = QColor( 0, 128, 128 )
    DARK_MAGENTA     = QColor( 128, 0, 128 )
    DARK_YELLOW      = QColor( 128, 128, 0 )
    
    DARK_ORANGE      = QColor( 128, 64, 0 )
    DARK_FUSCHIA     = QColor( 128, 0, 64 )
    DARK_LIME        = QColor( 64, 128, 0 )
    DARK_SPRINGGREEN = QColor( 0, 128, 64 )
    DARK_PURPLE      = QColor( 64, 0, 128 )
    DARK_DODGERBLUE  = QColor( 64, 0, 128 )
    
    LIGHT_RED        = QColor( 255, 128, 128 )
    LIGHT_GREEN      = QColor( 128, 255, 128 )
    LIGHT_BLUE       = QColor( 128, 128, 255 )
    
    LIGHT_CYAN       = QColor( 128, 255, 255 )
    LIGHT_MAGENTA    = QColor( 255, 0, 255 )
    LIGHT_YELLOW     = QColor( 255, 255, 128 )


class Pens:
    BLACK            = QPen( Colours.BLACK )
    DARK_GRAY        = QPen( Colours.DARK_GRAY )
    GRAY             = QPen( Colours.GRAY )
    LIGHT_GRAY       = QPen( Colours.LIGHT_GRAY )
    WHITE            = QPen( Colours.WHITE )
    RED              = QPen( Colours.RED )
    GREEN            = QPen( Colours.GREEN )
    BLUE             = QPen( Colours.BLUE )
    CYAN             = QPen( Colours.CYAN )
    MAGENTA          = QPen( Colours.MAGENTA )
    YELLOW           = QPen( Colours.YELLOW )
    ORANGE           = QPen( Colours.ORANGE )
    FUSCHIA          = QPen( Colours.FUSCHIA )
    LIME             = QPen( Colours.LIME )
    SPRING_GREEN     = QPen( Colours.SPRING_GREEN )
    PURPLE           = QPen( Colours.PURPLE )
    DODGER_BLUE      = QPen( Colours.DODGER_BLUE )
    DARK_RED         = QPen( Colours.DARK_RED )
    DARK_GREEN       = QPen( Colours.DARK_GREEN )
    DARK_BLUE        = QPen( Colours.DARK_BLUE )
    DARK_CYAN        = QPen( Colours.DARK_CYAN )
    DARK_MAGENTA     = QPen( Colours.DARK_MAGENTA )
    DARK_YELLOW      = QPen( Colours.DARK_YELLOW )
    DARK_ORANGE      = QPen( Colours.DARK_ORANGE )
    DARK_FUSCHIA     = QPen( Colours.DARK_FUSCHIA )
    DARK_LIME        = QPen( Colours.DARK_LIME )
    DARK_SPRINGGREEN = QPen( Colours.DARK_SPRINGGREEN )
    DARK_PURPLE      = QPen( Colours.DARK_PURPLE )
    DARK_DODGERBLUE  = QPen( Colours.DARK_DODGERBLUE )
    LIGHT_RED        = QPen( Colours.LIGHT_RED )
    LIGHT_GREEN      = QPen( Colours.LIGHT_GREEN )
    LIGHT_BLUE       = QPen( Colours.LIGHT_BLUE )
    LIGHT_CYAN       = QPen( Colours.LIGHT_CYAN )
    LIGHT_MAGENTA    = QPen( Colours.LIGHT_MAGENTA )
    LIGHT_YELLOW     = QPen( Colours.LIGHT_YELLOW )

class Brushes:
    BLACK            = QBrush( Colours.BLACK )
    DARK_GRAY        = QBrush( Colours.DARK_GRAY )
    GRAY             = QBrush( Colours.GRAY )
    LIGHT_GRAY       = QBrush( Colours.LIGHT_GRAY )
    WHITE            = QBrush( Colours.WHITE )
    RED              = QBrush( Colours.RED )
    GREEN            = QBrush( Colours.GREEN )
    BLUE             = QBrush( Colours.BLUE )
    CYAN             = QBrush( Colours.CYAN )
    MAGENTA          = QBrush( Colours.MAGENTA )
    YELLOW           = QBrush( Colours.YELLOW )
    ORANGE           = QBrush( Colours.ORANGE )
    FUSCHIA          = QBrush( Colours.FUSCHIA )
    LIME             = QBrush( Colours.LIME )
    SPRING_GREEN     = QBrush( Colours.SPRING_GREEN )
    PURPLE           = QBrush( Colours.PURPLE )
    DODGER_BLUE      = QBrush( Colours.DODGER_BLUE )
    DARK_RED         = QBrush( Colours.DARK_RED )
    DARK_GREEN       = QBrush( Colours.DARK_GREEN )
    DARK_BLUE        = QBrush( Colours.DARK_BLUE )
    DARK_CYAN        = QBrush( Colours.DARK_CYAN )
    DARK_MAGENTA     = QBrush( Colours.DARK_MAGENTA )
    DARK_YELLOW      = QBrush( Colours.DARK_YELLOW )
    DARK_ORANGE      = QBrush( Colours.DARK_ORANGE )
    DARK_FUSCHIA     = QBrush( Colours.DARK_FUSCHIA )
    DARK_LIME        = QBrush( Colours.DARK_LIME )
    DARK_SPRINGGREEN = QBrush( Colours.DARK_SPRINGGREEN )
    DARK_PURPLE      = QBrush( Colours.DARK_PURPLE )
    DARK_DODGERBLUE  = QBrush( Colours.DARK_DODGERBLUE )
    LIGHT_RED        = QBrush( Colours.LIGHT_RED )
    LIGHT_GREEN      = QBrush( Colours.LIGHT_GREEN )
    LIGHT_BLUE       = QBrush( Colours.LIGHT_BLUE )
    LIGHT_CYAN       = QBrush( Colours.LIGHT_CYAN )
    LIGHT_MAGENTA    = QBrush( Colours.LIGHT_MAGENTA )
    LIGHT_YELLOW     = QBrush( Colours.LIGHT_YELLOW )


def interpolate_float( a: float, b: float, fb: float ) -> float:
    return a + (b - a) * fb


def interpolate_int( a: int, b: int, fb: float ) -> int:
    return int( interpolate_float( a, b, fb ) )


def interpolate_colours( a: QColor, b: QColor, fb: float ) -> QColor:
    ca = interpolate_int( a.alpha(), b.alpha(), fb )
    cr = interpolate_int( a.red(), b.red(), fb )
    cg = interpolate_int( a.green(), b.green(), fb )
    cb = interpolate_int( a.blue(), b.blue(), fb )
    return QColor( cr, cg, cb, ca )

def average_colour( the_list ):
    r = sum( x.red() for x in the_list ) // len( the_list )
    g = sum( x.green() for x in the_list ) // len( the_list )
    b = sum( x.blue() for x in the_list ) // len( the_list )
    return QColor( r, g, b )


def random_colour():
    return QColor(randint(0,255),randint(0,255),randint(0,255))