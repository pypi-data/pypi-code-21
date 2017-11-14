"""
Helper functions for CLI-based plugins.
"""

from enum import Enum
from typing import List, Optional, Union

from colorama import Back, Fore, Style
from flags import Flags

from intermake.engine import constants, constants as mcmd_constants, m_print_helper
from intermake.engine.environment import MCMD, MENV
from intermake.engine.plugin import Plugin
from intermake.hosts.base import ERunMode, PluginHost
from mhelper import SwitchError, file_helper, string_helper


__print_banner_displayed = False


def print_description( description, keywords ):
    """
    Prints the `description` nicely, highlighting the specified `keywords`.
    """
    desc = highlight_keywords( description, keywords )
    
    for line in m_print_helper.wrap( desc, MENV.host.console_width() ):
        MCMD.print( line )


def print_self():
    """
    Prints the help of the calling plugin.
    """
    result = [ ]
    get_details( result, MCMD.plugin )
    MCMD.print( "\n".join( result ) )


def get_details_text( plugin: Plugin ):
    """
    Gets the help of the specified plugin.
    """
    result = [ ]
    get_details( result, plugin )
    return "\n".join( result )


def get_details( result: List[ str ], plugin: Plugin, show_quick: bool = False ):
    """
    Prints the details on an Plugin to the current progress reporter.
    """
    type_ = ""  # plugin.get_plugin_type()
    
    if file_helper.is_windows():
        LIGHT_BG = Back.BLACK
    else:
        LIGHT_BG = Back.LIGHTBLACK_EX
    
    type_colour = Style.RESET_ALL + Back.CYAN + Fore.BLACK
    bar_colour = LIGHT_BG + Style.DIM
    deco_colour = type_colour
    
    name = MENV.host.translate_name( plugin.name )  # type:str
    
    name_colour_extra = ""
    
    if not plugin.is_visible:
        name_colour_extra = Fore.RED
    elif plugin.is_highlighted:
        name_colour_extra = Fore.YELLOW
    
    env = MENV
    line_width = env.host.console_width
    
    result_b = [ ]
    
    if show_quick:
        name = name.ljust( 20 )
        prefix = Fore.LIGHTBLACK_EX + Style.DIM + "::" + Style.RESET_ALL
        
        result_b.append( prefix + " " + type_colour + type_ + Style.RESET_ALL + " " + constants.COL_ITEM + name_colour_extra + name + constants.COLX + deco_colour + constants.COLX + " -" )
        
        line = plugin.get_description().strip()
        line = env.host.substitute_text( line )
        
        line = line.split( "\n", 1 )[ 0 ]
        
        line = string_helper.fix_width( line, line_width - len(name) - 10 )
        
        line = highlight_keywords( line, plugin, constants.COL_CMD, constants.COLX + Style.DIM )
        
        result_b.append( " " + Style.DIM + line + constants.COLX + " " + prefix )
        
        result.append( "".join( result_b ) )
        
        return
    
    DESC_INDENT = 4
    
    ARG_INDENT = 8
    ARG_DESC_INDENT = 30
    
    DESC_INDENT_TEXT = " " * DESC_INDENT
    
    result.append( constants.COL_TITLE
                   + "  "
                   + bar_colour + "_"
                   + constants.COLX + constants.COL_TITLE + name_colour_extra + name
                   + bar_colour + "_" * (line_width - len( name ) - len( type_ ) - 1)
                   + deco_colour
                   + type_colour + type_
                   + constants.COLX )
    
    result.append( Style.DIM + "  Aliases: " + ", ".join( x for x in plugin.names if x != name ) + Style.RESET_ALL )
    
    #
    # DESCRIPTION
    #
    desc = plugin.get_description()
    desc = format_md( desc, env, plugin )
    
    for line in m_print_helper.wrap( desc, line_width - DESC_INDENT ):
        result.append( DESC_INDENT_TEXT + line + Style.RESET_ALL )
    
    #
    # ARGUMENTS
    #
    extra = False
    
    for arg in plugin.args:
        desc = arg.description or (arg.type_description + (" (default = " + str( arg.default ) + ")" if arg.default is not None else ""))
        desc = format_md( desc, env, plugin )
        
        t = arg.annotation
        
        viable_subclass_type = t.get_indirectly_below( Enum ) or t.get_indirectly_below( Flags )
        
        if viable_subclass_type is not None:
            desc += constants.COLX
            
            for k in viable_subclass_type.__dict__.keys():
                if not k.startswith( "_" ):
                    desc += "\n" + Fore.MAGENTA + " * " + constants.COL_CMD + k + constants.COLX
            
            desc += constants.COLX
            extra = True
        
        arg_name = constants.COL_ARG + MENV.host.translate_name( arg.name ) + constants.COLX + "\n" + Fore.LIGHTBLACK_EX
        
        default_text = str( arg.default ) if arg.default is not None else ""
        
        arg_name += "  " + default_text + constants.COLX
        
        desc += "\n"
        
        m_print_helper.print_box( result.append, ARG_INDENT, ARG_DESC_INDENT, line_width, arg_name, desc )
    
    if extra:
        result.append( "" )
        result.append( "    " + Fore.MAGENTA + "*" + constants.COLX + " Specify the argument when you call " + constants.COL_CMD + "help" + constants.COLX + " to obtain the full details for these values." )
    
    result.append( "" )


def format_md( desc, env, plugin ):
    desc = env.host.substitute_text( desc )
    desc = highlight_keywords( desc, plugin )
    desc = string_helper.highlight_quotes( desc, "`", "`", constants.COL_CMD, constants.COLX )
    desc = string_helper.highlight_quotes( desc, "'", "'", Fore.BLUE, constants.COLX )
    return desc


def highlight_keywords( desc: Union[ str, bytes ], plugin_or_list, highlight = constants.COL_ARG, normal = constants.COLX ):
    """
    Highlights the keywords in a plugin's description.
    :param desc:        Source string 
    :param plugin_or_list:      Either a plugin to get the keywords from, or a list of keywords.
    :param highlight:   Highlight colour 
    :param normal:      Normal colour 
    :return:            Modified string 
    """
    from intermake.engine.plugin import Plugin
    if isinstance( plugin_or_list, Plugin ):
        args = (z.name for z in plugin_or_list.args)
    else:
        args = plugin_or_list
    
    for arg in args:
        desc = desc.replace( "`" + arg + "`", highlight + arg + normal )
    
    return desc


def format_kv( key: str, value: Optional[ object ], spacer = "=" ):
    """
    Prints a bullet-pointed key-value pair to STDOUT
    """
    return "* " + constants.COL_KEY + key + Fore.LIGHTBLACK_EX + Style.DIM + "." * (40 - len( key )) + constants.COLX + " " + spacer + " " + constants.COL_VAL + str( value ) + constants.COLX


def print_value( value: str ):
    """
    Prints a bullet-pointed value pair to STDOUT
    """
    MCMD.print( "* " + constants.COL_ITEM + value + constants.COLX )


def print_banner( launch_type ) -> bool:
    """
    Prints a welcome message
    """
    if launch_type == ERunMode.ARG:
        return False
    
    global __print_banner_displayed
    assert isinstance( launch_type, ERunMode )
    env = MENV
    
    host = env.host  # type: PluginHost
    
    if not host.host_settings.welcome_message:
        return False
    
    width = host.console_width
    
    FORE_F = Fore.YELLOW
    FORE_B = Back.YELLOW
    BACK_F = Fore.BLUE
    BACK_B = Back.BLUE
    BOX_START_1 = Style.RESET_ALL + BACK_F + BACK_B
    BOX_START_2 = Style.RESET_ALL + FORE_F + BACK_B
    BOX_END = Style.RESET_ALL + BACK_F + "▖" + Style.RESET_ALL
    FINAL_LINE = Style.RESET_ALL + FORE_B + BACK_F
    FINAL_LINE_HIGHLIGHT = Style.RESET_ALL + Fore.RED + FORE_B
    
    switched_text = "changed to" if __print_banner_displayed else "is"
    
    if launch_type == ERunMode.ARG:
        pre_line = "Mode {} command line arguments".format( switched_text )
        help_cmd = "help"
        help_lst = "cmdlist"
    elif launch_type == ERunMode.CLI:
        pre_line = "Mode {} command line interface".format( switched_text )
        help_cmd = "help"
        help_lst = "cmdlist"
    elif launch_type == ERunMode.PYI:
        pre_line = "Mode {} Python interactive".format( switched_text )
        help_cmd = "help()"
        help_lst = "cmdlist()"
    elif launch_type == ERunMode.PYS:
        pre_line = "Mode {} automated Python script".format( switched_text )
        help_cmd = env.abv_name + ".help()"
        help_lst = env.abv_name + ".cmdlist()"
    elif launch_type == ERunMode.GUI:
        pre_line = "Mode {} graphical user interface".format( switched_text )
        help_cmd = ""
        help_lst = ""
    else:
        raise SwitchError( "launch_type", launch_type )
    
    help = FINAL_LINE + "Use " + FINAL_LINE_HIGHLIGHT + help_cmd + FINAL_LINE + " for help and " + FINAL_LINE_HIGHLIGHT + help_lst + FINAL_LINE + " to view commands."
    help = m_print_helper.ansi_ljust( help, " ", width ) + Style.RESET_ALL
    
    prefix = mcmd_constants.INFOLINE_SYSTEM
    prefix_s = mcmd_constants.INFOLINE_SYSTEM_CONTINUED
    
    if not __print_banner_displayed:
        box_width = width - 3
        print( prefix + BOX_START_1 + "█" * box_width + BOX_END )
        print( prefix_s + BOX_START_1 + "██" + string_helper.centre_align( " {} ".format( env.name.upper() ), box_width - len( env.version ) - 2, "█", prefix = BOX_START_2, suffix = BOX_START_1 ) + BOX_START_2 + " " + env.version + " " + BOX_START_1 + "█" + BOX_END )
        print( prefix_s + BOX_START_1 + "█" * box_width + "██" + BOX_END )
        
        if MENV.version.startswith( "0." ):
            print( prefix_s + FINAL_LINE + Fore.RED + "Alpha release. Not all features may work correctly. The API may change.".ljust( width ) + Style.RESET_ALL )
    else:
        print( prefix_s + BOX_START_1 + " " * width + "   " + Style.RESET_ALL )
    
    if pre_line:
        print( prefix_s + FINAL_LINE + m_print_helper.ansi_ljust( pre_line, " ", width ) + Style.RESET_ALL )
    
    if help_cmd:
        print( prefix_s + help )
    
    if not __print_banner_displayed:
        print( prefix_s )
        print( prefix_s + "WORKSPACE: " + MENV.local_data.get_workspace() )
        print( prefix_s )
    
    __print_banner_displayed = True
    
    return True


def highlight_quotes( text ):
    text = string_helper.highlight_quotes( text, "`", "`", mcmd_constants.COL_CMD, Style.RESET_ALL )
    return text
