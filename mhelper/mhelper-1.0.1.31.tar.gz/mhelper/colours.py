class Colour:
    def __init__( self, r, g, b ):
        self.r = r
        self.g = g
        self.b = b
    
    @property
    def html(self):
        return "#{0:02x}{1:02x}{2:02x}".format( self.r, self.g, self.b )


BLACK = Colour( 0, 0, 0 )
DARK_GRAY = Colour( 64, 64, 64 )
GRAY = Colour( 128, 128, 128 )
LIGHT_GRAY = Colour( 192, 192, 192 )
WHITE = Colour( 255, 255, 255 )

RED = Colour( 255, 0, 0 )
GREEN = Colour( 0, 255, 0 )
BLUE = Colour( 0, 0, 255 )

CYAN = Colour( 0, 255, 255 )
MAGENTA = Colour( 255, 0, 255 )
YELLOW = Colour( 255, 255, 0 )

ORANGE = Colour( 255, 128, 0 )
FUSCHIA = Colour( 255, 0, 128 )
LIME = Colour( 128, 255, 0 )
SPRING_GREEN = Colour( 0, 255, 128 )
PURPLE = Colour( 128, 0, 255 )
DODGER_BLUE = Colour( 128, 0, 255 )

DARK_RED = Colour( 128, 0, 0 )
DARK_GREEN = Colour( 0, 128, 0 )
DARK_BLUE = Colour( 0, 0, 128 )

DARK_CYAN = Colour( 0, 128, 128 )
DARK_MAGENTA = Colour( 128, 0, 128 )
DARK_YELLOW = Colour( 128, 128, 0 )

DARK_ORANGE = Colour( 128, 64, 0 )
DARK_FUSCHIA = Colour( 128, 0, 64 )
DARK_LIME = Colour( 64, 128, 0 )
DARK_SPRINGGREEN = Colour( 0, 128, 64 )
DARK_PURPLE = Colour( 64, 0, 128 )
DARK_DODGERBLUE = Colour( 64, 0, 128 )

LIGHT_RED = Colour( 255, 128, 128 )
LIGHT_GREEN = Colour( 128, 255, 128 )
LIGHT_BLUE = Colour( 128, 128, 255 )

LIGHT_CYAN = Colour( 128, 255, 255 )
LIGHT_MAGENTA = Colour( 255, 0, 255 )
LIGHT_YELLOW = Colour( 255, 255, 128 )
