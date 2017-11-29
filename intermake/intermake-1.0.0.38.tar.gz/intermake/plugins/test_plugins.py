from typing import Optional

from intermake.engine.environment import MCMD
from intermake.hosts.base import ERunMode
from intermake.hosts.console import ConsoleHost
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
def test_progress( fast: bool = False ):
    """
    Does nothing.
    
    :param fast: Does nothing faster
    """
    count = 1000000 if fast else 10000000
    
    with MCMD.action( "Doing some work for you!", count ) as action:
        for n in range( count ):
            action.increment()


@command( visibility = TEST )
def test_progress_2():
    """
    Does nothing.
    """
    count = 10000000
    
    with MCMD.action( "Doing some work for you!" ) as action:
        for n in range( count ):
            action.still_alive()


@command( names = ["test_banner", "hello"], visibility = TEST )
def test_banner( launch_type: Optional[ERunMode] = None ):
    """
    Tests the banner
    
    :param launch_type: Type to display banner for.
    """
    
    if launch_type is None:
        h = MCMD.host
        
        if isinstance( h, ConsoleHost ):
            launch_type = h.console_configuration.run_mode
        else:
            launch_type = ERunMode.GUI
    
    cli_helper.print_banner( launch_type, force = True )


@command( visibility = TEST )
def test_error():
    """
    Tests the error handling capabilities of the host
    """
    raise ValueError( "This is an error." )
