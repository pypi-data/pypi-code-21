"""
Helper functions for CLI-based plugins.
"""

from enum import Enum
from typing import List, Optional, Union

from flags import Flags

from intermake.engine import m_print_helper
from intermake.engine.environment import MCMD, MENV
from intermake.engine.plugin import Plugin
from intermake.hosts.base import ERunMode, PluginHost
from mhelper import SwitchError, string_helper
from intermake.engine.theme import Theme
from intermake.engine import constants


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
    result = []
    get_details( result, MCMD.plugin )
    MCMD.print( "\n".join( result ) )


def get_details_text( plugin: Plugin ):
    """
    Gets the help of the specified plugin.
    """
    result = []
    get_details( result, plugin )
    return "\n".join( result )


def get_details( result: List[str], plugin: Plugin, show_quick: bool = False ):
    """
    Prints the details on an Plugin to the current progress reporter.
    """
    type_ = ""  # plugin.get_plugin_type()
    
    type_colour = Theme.BOX_TITLE_RIGHT
    bar_colour = Theme.BORDER
    deco_colour = type_colour
    
    name = MENV.host.translate_name( plugin.name )  # type:str
    
    if not plugin.is_visible:
        name_colour_extra = Theme.SYSTEM_NAME
    elif plugin.is_highlighted:
        name_colour_extra = Theme.CORE_NAME
    else:
        name_colour_extra = Theme.COMMAND_NAME
    
    env = MENV
    line_width = env.host.console_width
    
    result_b = []
    
    if show_quick:
        name = name.ljust( 20 )
        prefix = Theme.BORDER + "::" + Theme.RESET
        
        result_b.append( prefix + " " + type_colour + type_ + Theme.RESET + " " + name_colour_extra + name + Theme.RESET + " -" )
        
        line = plugin.get_description().strip()
        line = env.host.substitute_text( line )
        
        line = line.split( "\n", 1 )[0]
        
        line = string_helper.fix_width( line, line_width - len( name ) - 10 )
        
        line = highlight_keywords( line, plugin, Theme.COMMAND_NAME, Theme.COMMENT )
        
        result_b.append( " " + Theme.COMMENT + line + Theme.RESET + " " + prefix )
        
        result.append( "".join( result_b ) )
        
        return
    
    DESC_INDENT = 4
    
    ARG_INDENT = 8
    ARG_DESC_INDENT = 30
    
    DESC_INDENT_TEXT = " " * DESC_INDENT
    
    result.append( "  "
                   + bar_colour + "_"
                   + name_colour_extra + name
                   + bar_colour + "_" * (line_width - len( name ) - len( type_ ) - 1)
                   + deco_colour
                   + type_colour + type_
                   + Theme.RESET )
    
    result.append( Theme.COMMENT + "  Aliases: " + ", ".join( x for x in plugin.names if x != name ) + Theme.RESET )
    
    #
    # DESCRIPTION
    #
    desc = plugin.get_description()
    desc = format_md( desc, env, plugin )
    
    for line in m_print_helper.wrap( desc, line_width - DESC_INDENT ):
        result.append( DESC_INDENT_TEXT + line + Theme.RESET )
    
    #
    # ARGUMENTS
    #
    extra = False
    
    for arg in plugin.args:
        desc = arg.description or (str( arg.annotation ) + (" (default = " + str( arg.default ) + ")" if arg.default is not None else ""))
        desc = format_md( desc, env, plugin )
        
        t = arg.annotation
        
        viable_subclass_type = t.get_indirectly_below( Enum ) or t.get_indirectly_below( Flags )
        
        if viable_subclass_type is not None:
            desc += Theme.RESET
            
            for k in viable_subclass_type.__dict__.keys():
                if not k.startswith( "_" ):
                    desc += "\n" + Theme.ENUMERATION + " * " + Theme.COMMAND_NAME + k + Theme.RESET
            
            desc += Theme.RESET
            extra = True
        
        arg_name = Theme.ARGUMENT_NAME + MENV.host.translate_name( arg.name ) + Theme.RESET + "\n" + Theme.COMMENT
        
        default_text = str( arg.default ) if arg.default is not None else ""
        
        arg_name += "  " + default_text + Theme.RESET
        
        desc += "\n"
        
        m_print_helper.print_box( result.append, ARG_INDENT, ARG_DESC_INDENT, line_width, arg_name, desc )
    
    if extra:
        result.append( "" )
        result.append( "    " + Theme.ENUMERATION + "*" + Theme.RESET + " Specify the argument when you call " + Theme.COMMAND_NAME + "help" + Theme.RESET + " to obtain the full details for these values." )
    
    result.append( "" )


def format_md( desc, env, plugin ):
    desc = env.host.substitute_text( desc )
    desc = highlight_keywords( desc, plugin )
    desc = string_helper.highlight_quotes( desc, "`", "`", Theme.EMPHASIS_EXTRA, Theme.RESET )
    desc = string_helper.highlight_quotes( desc, "«", "»", Theme.EMPHASIS, Theme.RESET )
    return desc


def highlight_keywords( desc: Union[str, bytes], plugin_or_list, highlight = None, normal = None ):
    """
    Highlights the keywords in a plugin's description.
    :param desc:        Source string 
    :param plugin_or_list:      Either a plugin to get the keywords from, or a list of keywords.
    :param highlight:   Highlight colour 
    :param normal:      Normal colour 
    :return:            Modified string 
    """
    if highlight is None:
        highlight = Theme.ARGUMENT_NAME
    
    if normal is None:
        normal = Theme.RESET
    
    from intermake.engine.plugin import Plugin
    if isinstance( plugin_or_list, Plugin ):
        args = (z.name for z in plugin_or_list.args)
    else:
        args = plugin_or_list
    
    for arg in args:
        desc = desc.replace( "`" + arg + "`", highlight + arg + normal )
    
    return desc


def format_kv( key: str, value: Optional[object], spacer = "=" ):
    """
    Prints a bullet-pointed key-value pair to STDOUT
    """
    return "* " + Theme.COMMAND_NAME + key + Theme.BORDER + " " + "." * (39 - len( key )) + Theme.RESET + " " + spacer + " " + Theme.VALUE + str( value ) + Theme.RESET


def print_value( value: str ):
    """
    Prints a bullet-pointed value pair to STDOUT
    """
    MCMD.print( "* " + Theme.COMMAND_NAME + value + Theme.RESET )


def print_banner( launch_type, force = False ) -> bool:
    """
    Prints a welcome message
    """
    if launch_type == ERunMode.ARG and not force:
        return False
    
    global __print_banner_displayed
    assert isinstance( launch_type, ERunMode )
    env = MENV
    
    host = env.host  # type: PluginHost
    
    if not host.host_settings.welcome_message and not force:
        return False
    
    width = min(host.console_width, 100)
    box_width = width - 3
    
    BOX_END = Theme.BANNER_END_OF_THE_LINE + "▖" + Theme.RESET
    
    switched_text = "changed to" if __print_banner_displayed else "is"
    
    if launch_type == ERunMode.ARG:
        pre_line = "ARG".format( switched_text )
        help_cmd = "help"
        help_lst = "cmdlist"
    elif launch_type == ERunMode.CLI:
        pre_line = "CLI".format( switched_text )
        help_cmd = "help"
        help_lst = "cmdlist"
    elif launch_type == ERunMode.PYI:
        pre_line = "PYI".format( switched_text )
        help_cmd = "help()"
        help_lst = "cmdlist()"
    elif launch_type == ERunMode.PYS:
        pre_line = "PYS".format( switched_text )
        help_cmd = env.abv_name + ".help()"
        help_lst = env.abv_name + ".cmdlist()"
    elif launch_type == ERunMode.GUI:
        pre_line = "GUI".format( switched_text )
        help_cmd = ""
        help_lst = ""
    else:
        raise SwitchError( "launch_type", launch_type )
    
    help = Theme.BANNER_MAIN + MENV.name + "/" + pre_line + ". Use " + Theme.BANNER_COMMAND_NAME + help_cmd + Theme.BANNER_MAIN + " for help and " + Theme.BANNER_COMMAND_NAME + help_lst + Theme.BANNER_MAIN + " to view commands."
    help = m_print_helper.ansi_ljust( help, " ", width ) + Theme.RESET
    
    prefix = constants.INFOLINE_SYSTEM
    prefix_s = constants.INFOLINE_SYSTEM_CONTINUED
    
    if not __print_banner_displayed:
        print( prefix + Theme.BANNER_ZERO + "█" * box_width + BOX_END )
        print( prefix_s + Theme.BANNER_ZERO + "██" + string_helper.centre_align( " {} ".format( env.name.upper() ), box_width - len( env.version ) - 2, "█", prefix = Theme.BANNER_REVERSED, suffix = Theme.BANNER_ZERO ) + Theme.BANNER_REVERSED + " " + env.version + " " + Theme.BANNER_ZERO + "█" + BOX_END )
        print( prefix_s + Theme.BANNER_ZERO + "█" * box_width + "██" + BOX_END )
    
    else:
        print( prefix_s + Theme.BANNER_MAIN + " " * box_width + "   " + Theme.RESET )
    
    if help_cmd:
        print( prefix_s + help )
    
    if not __print_banner_displayed:
        print( prefix_s + Theme.BANNER_MAIN + ("The current workspace is '" + MENV.local_data.get_workspace() + "'").ljust( width ) + Theme.RESET )
        
        if MENV.version.startswith( "0." ):
            print( prefix_s + Theme.BANNER_MAIN + "This application is in development; not all features may work correctly and the API may change.".ljust( width ) + Theme.RESET )
        
    __print_banner_displayed = True
    
    return True


def highlight_quotes( text ):
    text = string_helper.highlight_quotes( text, "`", "`", Theme.COMMAND_NAME, Theme.RESET )
    return text
