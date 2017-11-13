"""
intermake package entry-point.
See `readme.md` for details.
"""

from intermake.engine.async_result import AsyncResult
from intermake.engine.environment import start, MENV, MCMD, register
from intermake.engine.function_inspector import NOT_PROVIDED
from intermake.engine.plugin_manager import PluginManager
from intermake.engine.progress_reporter import ActionHandler
from intermake.helpers.table_draw import Table

from intermake.hosts.frontends.gui_qt.designer import resources
from intermake.hosts.base import ResultsExplorer, create_simple_host_provider, create_simple_host_provider_from_class, ERunMode
from intermake.hosts.console import ConsoleHost
from intermake.plugins.command_plugin import command, CommandPlugin, help_command
from intermake.engine.constants import EThread, EStream, OUVisibility, mandated
from intermake.engine.plugin_arguments import ArgsKwargs, PluginArg, PluginArgValue, PluginArgValueCollection, HFunctionParameterType
from intermake.plugins.setter_plugin import SetterPlugin, setter_command
from intermake.engine import cli_helper, function_inspector
from intermake.engine.plugin import Plugin
from intermake.engine.mandate import Mandate
from intermake.plugins import visibilities
from intermake.plugins.visibilities import VisibilityClass
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo, NamedValue, as_visualisable
from intermake.plugins import console_explorer
from intermake.engine import m_print_helper
from intermake.engine import m_print_helper, constants, environment, constants
from intermake.plugins import visibilities
from intermake.visualisables.visualisable_operations import PathToVisualisable


def __setup() -> None:
    """
    Initialise stuff
    """
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Python version ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    import sys
    version = sys.version_info
    if version[0] != 3 and version[1] < 6:
        raise ValueError( "You are using Python version {}.{}, but this application requires version 3.6.".format( version[0], version[1] ) )
    
    if version[1] != 6:
        import warnings
        warnings.warn( "You are using Python version {}.{}, but this application was designed for version 3.6.".format( version[0], version[1] ), UserWarning )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ UTF-8 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    from mhelper import string_helper
    string_helper.assert_unicode()
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Colorama ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    import colorama
    colorama.init()
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Coercion ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    import intermake.helpers.coercion_extensions
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Editorium ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # (defer through function so we don't have to load Qt)
    def __editors() -> type:
        from intermake.hosts.frontends.gui_qt.editorium_extensions import Editor_Visualisable
        return Editor_Visualisable
    
    
    import editorium
    editorium.register( __editors )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ intermake defaults ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    MENV.host = ConsoleHost.get_default( ERunMode.PYS )
    MENV.plugins.legacy_load_namespace( plugins )


__setup()
