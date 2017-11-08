from intermake.engine.environment import MCMD
from intermake.plugins.command_plugin import command
from intermake.plugins.visibilities import TEST
from intermake.engine import cli_helper
from mhelper import string_helper


@command( visibility = TEST )
def console_width():
    """
    Prints the console width.
    """
    w = MCMD.host.console_width - 4
    msg = "Console width hint is {}. This banner is the same size as the console width hint.".format( MCMD.host.console_width )
    msg = string_helper.max_width( msg, w - 4 )
    MCMD.print( "+" * w )
    MCMD.print( "+ " + msg + " " * (w - len( msg ) - 4) + " +" )
    MCMD.print( "+" * w )


@command( visibility = TEST )
def py_modules():
    """
    Lists the Python modules
    """
    for x in sys.modules.keys():
        cli_helper.print_value( x )


@command( visibility = TEST )
def test_progress():
    """
    Does nothing.
    """
    count = 10000000
    
    with MCMD.action( "Doing some work for you!", count ) as action:
        for n in range( count ):
            action.increment()
